# API Reference

## POST /api/chat

Stream a chat response with RAG context.

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "message": "How do I configure the database?",
  "url": "https://example.com/docs/database"
}
```

**Response:** Server-Sent Events (SSE) stream

Each event is a JSON object with the following structure:

```json
{"type": "citations", "data": [{"url": "...", "title": "..."}]}
{"type": "token", "data": "Hello"}
{"type": "done", "data": ""}
```

## POST /api/sessions

Create a new chat session.

**Response:**
```json
{
  "id": "uuid-string",
  "title": "New Chat"
}
```

## GET /api/sessions

List all chat sessions.

**Response:**
```json
[
  {"id": "uuid-string", "title": "Database Configuration", "updated_at": "..."}
]
```

## GET /api/sessions/{session_id}/messages

Get messages for a session.

**Response:**
```json
[
  {"role": "user", "content": "How do I configure the database?"},
  {"role": "assistant", "content": "To configure the database..."}
]
```
