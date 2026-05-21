"""
Offline document ingestion pipeline.

Usage:
    docker compose exec backend python scripts/ingest.py [--dir /app/scripts/sample_docs]
"""

import argparse
import asyncio
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import AsyncOpenAI
from sqlalchemy import text

# Add parent to path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.database import async_session
from app.models import Document


def compute_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def parse_markdown_frontmatter(content: str) -> tuple[str, dict]:
    """Extract frontmatter-like metadata from first line heading."""
    meta: dict = {}
    lines = content.strip().split("\n")
    if lines and lines[0].startswith("# "):
        meta["title"] = lines[0][2:].strip()
    return content, meta


async def ingest_directory(docs_dir: str) -> dict[str, int]:
    """Read all markdown/html files, chunk them, embed, and bulk insert."""
    client = AsyncOpenAI(
        api_key=settings.openai_api_key, base_url=settings.openai_base_url
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""],
    )

    docs_path = Path(docs_dir)
    supported_suffixes = {".md", ".html", ".htm", ".txt"}
    files = [f for f in docs_path.rglob("*") if f.suffix in supported_suffixes]

    if not files:
        print(f"No supported files found in {docs_dir}")
        return {"files": 0, "chunks": 0, "inserted": 0}

    print(f"Found {len(files)} file(s) to process.")

    all_rows: list[dict] = []
    file_count = 0

    for filepath in files:
        content = filepath.read_text(encoding="utf-8")
        relative_path = str(filepath.relative_to(docs_path))

        content, meta = parse_markdown_frontmatter(content)
        if "title" not in meta:
            meta["title"] = relative_path
        meta["source"] = relative_path

        chunks = splitter.split_text(content)
        file_count += 1
        print(f"  {relative_path}: {len(chunks)} chunk(s)")

        for chunk in chunks:
            all_rows.append(
                {
                    "content": chunk,
                    "metadata_": meta,
                    "content_hash": compute_content_hash(chunk),
                }
            )

    if not all_rows:
        print("No chunks produced.")
        return {"files": file_count, "chunks": 0, "inserted": 0}

    # Batch embed (max 1000 per call to respect API limits)
    batch_size = 100
    total_embedded = 0

    for i in range(0, len(all_rows), batch_size):
        batch = all_rows[i : i + batch_size]
        texts = [r["content"] for r in batch]

        response = await client.embeddings.create(
            model=settings.embedding_model, input=texts
        )

        for j, emb in enumerate(response.data):
            batch[j]["embedding"] = emb.embedding

        total_embedded += len(batch)
        print(
            f"  Embedded {total_embedded}/{len(all_rows)} chunks "
            f"(batch {i // batch_size + 1})"
        )

    # Bulk upsert
    insert_count = 0
    async with async_session() as session:
        for i in range(0, len(all_rows), batch_size):
            batch = all_rows[i : i + batch_size]
            values_parts: list[str] = []
            params: dict = {}

            for j, row in enumerate(batch):
                rid = str(uuid.uuid4())
                values_parts.append(
                    f"(:id_{j}, :content_{j}, :meta_{j}, :embed_{j}, :hash_{j})"
                )
                params.update(
                    {
                        f"id_{j}": rid,
                        f"content_{j}": row["content"],
                        f"meta_{j}": json.dumps(row["metadata_"]),
                        f"embed_{j}": row["embedding"],
                        f"hash_{j}": row["content_hash"],
                    }
                )

            stmt = text(
                f"""
                INSERT INTO documents (id, content, metadata_, embedding, content_hash)
                VALUES {', '.join(values_parts)}
                ON CONFLICT (content_hash) DO UPDATE SET
                    metadata_ = EXCLUDED.metadata_,
                    embedding = EXCLUDED.embedding
                """
            )
            await session.execute(stmt, params)
            insert_count += len(batch)

        await session.commit()

    result = {"files": file_count, "chunks": len(all_rows), "inserted": insert_count}
    print(f"Done: {result}")
    return result


async def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest documents into ChatRAG")
    parser.add_argument(
        "--dir",
        default=str(Path(__file__).resolve().parent / "sample_docs"),
        help="Directory containing markdown/html files",
    )
    args = parser.parse_args()

    if not settings.openai_api_key or settings.openai_api_key.startswith("sk-your-"):
        print("ERROR: Please set OPENAI_API_KEY in .env file.")
        sys.exit(1)

    await ingest_directory(args.dir)


if __name__ == "__main__":
    asyncio.run(main())
