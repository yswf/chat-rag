<script setup lang="ts">
import { onMounted } from "vue";
import ChatSidebar from "./components/ChatSidebar.vue";
import ChatMain from "./components/ChatMain.vue";
import { useChat } from "./composables/useChat";
import { useHostContext } from "./composables/useHostContext";

const {
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
} = useChat();

const { context, isEmbedded } = useHostContext();

onMounted(() => {
  loadSessions();
});

function handleSend(msg: string): void {
  sendMessage(msg, context.value?.url);
}
</script>

<template>
  <div
    :class="[
      'flex h-screen overflow-hidden',
      isEmbedded ? '' : 'bg-gray-50',
    ]"
  >
    <ChatSidebar
      v-if="!isEmbedded"
      :sessions="sessions"
      :current-session-id="currentSessionId"
      @select="selectSession"
      @new="createSession()"
      @delete="deleteSession"
    />

    <ChatMain
      :messages="messages"
      :is-streaming="isStreaming"
      :stream-content="streamContent"
      :citations="citations"
      :error="error"
      :context="context"
      :is-embedded="isEmbedded"
      @send="handleSend"
    />
  </div>
</template>
