<script setup lang="ts">
import { ref, watch, nextTick } from "vue";
import type { ChatMessage, Citation, HostContext } from "../types";
import ChatMessageBubble from "./ChatMessageBubble.vue";
import ChatInput from "./ChatInput.vue";

const props = defineProps<{
  messages: ChatMessage[];
  isStreaming: boolean;
  streamContent: string;
  citations: Citation[];
  error: string | null;
  context: HostContext | null;
  isEmbedded: boolean;
}>();

const emit = defineEmits<{
  send: [content: string];
}>();

const scrollContainer = ref<HTMLElement | null>(null);

watch(
  () => [props.messages.length, props.streamContent],
  async () => {
    await nextTick();
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
    }
  },
  { deep: true }
);

function renderMarkdown(text: string): string {
  let html = text
    .replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/^### (.+)$/gm, "<h4>$1</h4>")
    .replace(/^## (.+)$/gm, "<h3>$1</h3>")
    .replace(/^# (.+)$/gm, "<h2>$1</h2>")
    .replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>'
    )
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br>");
  return `<p>${html}</p>`;
}
</script>

<template>
  <div class="flex-1 flex flex-col min-w-0">
    <!-- Context banner -->
    <div
      v-if="context?.url"
      class="bg-amber-50 border-b border-amber-200 px-4 py-1.5 text-xs text-amber-800 flex items-center gap-2"
    >
      <span>📄 Context: {{ context.title || context.url }}</span>
    </div>

    <!-- Messages -->
    <div ref="scrollContainer" class="flex-1 overflow-y-auto px-6 py-4">
      <div class="max-w-4xl mx-auto">
        <!-- Empty state -->
        <div
          v-if="messages.length === 0 && !isStreaming"
          class="flex items-center justify-center h-full py-20"
        >
          <div class="text-center text-gray-400">
            <p class="text-2xl mb-2">📚</p>
            <p class="text-lg font-medium">ChatRAG</p>
            <p class="text-sm mt-1">
              Ask questions about the documentation
            </p>
          </div>
        </div>

        <!-- Message bubbles -->
        <template v-for="msg in messages" :key="msg.id || msg.created_at">
          <ChatMessageBubble :message="msg" />
        </template>

        <!-- Streaming preview -->
        <div v-if="isStreaming && streamContent" class="flex gap-3 py-4">
          <div class="w-8 h-8 rounded-full bg-gray-700 text-white flex items-center justify-center text-sm font-medium shrink-0">
            AI
          </div>
          <div class="max-w-[75%] rounded-xl px-4 py-3 bg-gray-100 text-gray-900">
            <div v-html="renderMarkdown(streamContent)" class="prose prose-sm max-w-none" />
            <span class="inline-block w-2 h-4 bg-blue-600 animate-pulse ml-0.5 align-middle" />
          </div>
        </div>

        <!-- Citations preview during streaming -->
        <div
          v-if="isStreaming && citations.length > 0"
          class="ml-11 mb-4"
        >
          <div class="text-xs text-gray-500">
            <span class="font-medium">Sources found:</span>
            <span v-for="(cite, i) in citations" :key="i" class="ml-2">
              {{ cite.title || `Source ${i + 1}` }}{{ i < citations.length - 1 ? ',' : '' }}
            </span>
          </div>
        </div>

        <!-- Error -->
        <div
          v-if="error"
          class="mx-4 my-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700"
        >
          {{ error }}
        </div>
      </div>
    </div>

    <!-- Input -->
    <ChatInput :is-streaming="isStreaming" @send="emit('send', $event)" />
  </div>
</template>
