# ChatRAG Documentation

ChatRAG is an open-source document chat website similar to chat-langchain. It allows you to embed a chatbot into any documentation website via an iframe, providing page-level context-aware Q&A.

## Features

- Document ingestion pipeline with automatic chunking and vector embeddings
- Hybrid vector search with metadata filtering using PostgreSQL + pgvector
- Streaming chat responses via Server-Sent Events (SSE)
- Cross-origin iframe communication for embedded chat
- Session memory management for contextual conversations

## Architecture

The system consists of three main components:

1. **Backend (FastAPI + Python)** - API server handling document retrieval, chat streaming, and session management
2. **Frontend (Vue 3 + TypeScript)** - Chat UI with markdown rendering and citation display
3. **Database (PostgreSQL + pgvector)** - Vector storage with cosine similarity search

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your OpenAI API key
3. Run `docker compose up -d`
4. Ingest your documents using the ingestion script
5. Open the frontend and start chatting
