import { ref, type Ref } from "vue";
import type { ChatMessage, ChatSession, Citation, SSEEvent } from "../types";

export function useChat() {
  const sessions = ref<ChatSession[]>([]);
  const currentSessionId = ref<string | null>(null);
  const messages = ref<ChatMessage[]>([]);
  const isStreaming = ref(false);
  const streamContent = ref("");
  const citations = ref<Citation[]>([]);
  const error = ref<string | null>(null);

  async function loadSessions(): Promise<void> {
    const res = await fetch("/api/sessions");
    if (res.ok) sessions.value = await res.json();
  }

  async function createSession(): Promise<string> {
    const res = await fetch("/api/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "New Chat" }),
    });
    const session: ChatSession = await res.json();
    sessions.value.unshift(session);
    return session.id;
  }

  async function loadMessages(sessionId: string): Promise<void> {
    const res = await fetch(`/api/sessions/${sessionId}/messages`);
    if (res.ok) messages.value = await res.json();
  }

  async function selectSession(sessionId: string): Promise<void> {
    currentSessionId.value = sessionId;
    await loadMessages(sessionId);
  }

  async function sendMessage(
    content: string,
    parentUrl?: string | null
  ): Promise<void> {
    if (!content.trim() || isStreaming.value) return;

    error.value = null;
    streamContent.value = "";
    citations.value = [];

    // Add user message optimistically
    const userMsg: ChatMessage = {
      id: "",
      session_id: currentSessionId.value || "",
      role: "user",
      content,
      citations: null,
      created_at: new Date().toISOString(),
    };
    messages.value.push(userMsg);

    let sessionId = currentSessionId.value;
    if (!sessionId) {
      sessionId = await createSession();
      currentSessionId.value = sessionId;
    }

    isStreaming.value = true;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          message: content,
          url: parentUrl || null,
        }),
      });

      const reader = res.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const json = line.slice(6);
          try {
            const event: SSEEvent = JSON.parse(json);
            switch (event.type) {
              case "session_id":
                currentSessionId.value = event.data;
                break;
              case "citations":
                citations.value = event.data;
                break;
              case "token":
                streamContent.value += event.data;
                break;
              case "done":
                // Finalize
                messages.value.push({
                  id: "",
                  session_id: currentSessionId.value || "",
                  role: "assistant",
                  content: streamContent.value,
                  citations: citations.value,
                  created_at: new Date().toISOString(),
                });
                streamContent.value = "";
                citations.value = [];
                break;
              case "error":
                error.value = event.data;
                break;
            }
          } catch {
            // skip malformed JSON
          }
        }
      }
    } catch (e) {
      error.value = String(e);
    } finally {
      isStreaming.value = false;
      await loadSessions(); // refresh titles
    }
  }

  async function deleteSession(sessionId: string): Promise<void> {
    await fetch(`/api/sessions/${sessionId}`, { method: "DELETE" });
    sessions.value = sessions.value.filter((s) => s.id !== sessionId);
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null;
      messages.value = [];
    }
  }

  return {
    sessions,
    currentSessionId,
    messages,
    isStreaming,
    streamContent,
    citations,
    error,
    loadSessions,
    createSession,
    selectSession,
    sendMessage,
    deleteSession,
  };
}
