# ChatRAG - Open Source Document Chat Website

An open-source, free document Q&A website similar to [chat-langchain](https://github.com/langchain-ai/chat-langchain). It supports standalone use and iframe embedding to provide page-level context-aware Q&A for any documentation website.

## Features

- **Document Ingestion Pipeline** — Automatic chunking and vector embedding for Markdown / HTML docs
- **Hybrid Vector Search** — PostgreSQL + pgvector with cosine similarity and metadata filtering
- **Streaming Chat** — Server-Sent Events (SSE) for real-time AI responses
- **Session Memory** — Contextual multi-turn conversations persisted in PostgreSQL
- **Cross-Origin Embedding** — Embed the chatbot in any website via iframe with automatic context passing
- **Markdown Rendering** — Rich text rendering for AI responses with citation links

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│   Frontend   │────▶│   Backend    │────▶│  PostgreSQL +  │
│  Vue 3 + TS  │◀────│  FastAPI     │◀────│    pgvector    │
│   (Vite)     │ SSE │   (Python)   │     │                │
└──────────────┘     └──────────────┘     └────────────────┘
       │                      │
       │                      ▼
       │             ┌────────────────┐
       └────────────▶│   OpenAI API   │
                     │ (Embeddings +  │
                     │  Chat)         │
                     └────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key

### 1. Clone and Configure

```bash
git clone <your-repo-url>
cd chat-rag
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

### 2. Start Services

```bash
docker compose up -d
```

This starts three services:
- **db** — PostgreSQL 16 with pgvector (port 5432)
- **backend** — FastAPI server (port 8000)
- **frontend** — Vue 3 dev server (port 5173)

### 3. Ingest Documents

```bash
# Ingest sample docs
docker compose exec backend python scripts/ingest.py --dir /app/scripts/sample_docs

# Or ingest your own docs
docker compose exec backend python scripts/ingest.py --dir /app/scripts/your_docs
```

### 4. Open the App

Visit **http://localhost:5173** and start chatting.

## Embedding in Your Website

Add the following script to any webpage to show a floating chat button:

```html
<script src="http://localhost:5173/chatrag-embed.js" defer></script>
```

The script automatically:
1. Creates a floating button in the bottom-right corner
2. Detects the current page URL and title
3. Sends context to the chat iframe via `postMessage`

Update the `CHAT_URL` variable in `chatrag-embed.js` to point to your deployed frontend.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/chat` | Stream chat response (SSE) |
| GET/POST | `/api/sessions` | List / create chat sessions |
| GET/DELETE | `/api/sessions/{id}` | Get / delete a session |
| GET | `/api/sessions/{id}/messages` | Get session messages |

### SSE Event Types

```
data: {"type": "session_id", "data": "uuid"}
data: {"type": "citations", "data": [...]}
data: {"type": "token", "data": "Hello"}
data: {"type": "done", "data": ""}
data: {"type": "error", "data": "message"}
```

## Project Structure

```
chat-rag/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── config.py         # Settings (env vars)
│   │   ├── database.py       # Async engine & session
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic schemas
│   │   ├── services.py       # Retrieval & chat logic
│   │   └── routers/
│   │       ├── chat.py       # Streaming chat endpoint
│   │       └── sessions.py   # Session CRUD endpoints
│   └── scripts/
│       ├── ingest.py          # Document ingestion pipeline
│       └── sample_docs/       # Sample markdown documents
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── public/
    │   └── chatrag-embed.js   # Host website injection script
    └── src/
        ├── main.ts
        ├── App.vue
        ├── types.ts
        ├── composables/
        │   ├── useChat.ts         # Chat state management
        │   └── useHostContext.ts  # iframe postMessage listener
        └── components/
            ├── ChatSidebar.vue
            ├── ChatMain.vue
            ├── ChatMessageBubble.vue
            └── ChatInput.vue
```

## Tech Stack

- **Frontend:** Vue 3, TypeScript, Vite, Tailwind CSS
- **Backend:** Python 3.11, FastAPI, Pydantic V2
- **Database:** PostgreSQL 16 + pgvector
- **ORM:** SQLAlchemy 2.0 (async)
- **AI:** OpenAI API (embeddings + chat completions)
- **Deployment:** Docker Compose

## License

MIT
