export interface Citation {
  url: string | null;
  title: string | null;
  content: string | null;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  citations: Citation[] | null;
  created_at: string;
}

export interface HostContext {
  url: string;
  title: string;
  content: string;
}

export interface SSECitationsEvent {
  type: "citations";
  data: Citation[];
}

export interface SSETokenEvent {
  type: "token";
  data: string;
}

export interface SSESessionIdEvent {
  type: "session_id";
  data: string;
}

export interface SSEDoneEvent {
  type: "done";
  data: string;
}

export interface SSEErrorEvent {
  type: "error";
  data: string;
}

export type SSEEvent =
  | SSECitationsEvent
  | SSETokenEvent
  | SSESessionIdEvent
  | SSEDoneEvent
  | SSEErrorEvent;
