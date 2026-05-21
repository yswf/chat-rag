<script setup lang="ts">
import type { ChatMessage, Citation } from "../types";

defineProps<{
  message: ChatMessage;
}>();

function renderMarkdown(text: string): string {
  // Simple markdown rendering (no external lib needed)
  let html = text
    // Code blocks
    .replace(/```(\w*)\n([\s\S]*?)```/g, "<pre><code>$2</code></pre>")
    // Inline code
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    // Bold
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    // Headers
    .replace(/^### (.+)$/gm, "<h4>$1</h4>")
    .replace(/^## (.+)$/gm, "<h3>$1</h3>")
    .replace(/^# (.+)$/gm, "<h2>$1</h2>")
    // Links
    .replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener">$1</a>'
    )
    // Newlines
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n/g, "<br>");

  return `<p>${html}</p>`;
}
</script>

<template>
  <div class="flex gap-3 py-4" :class="message.role === 'user' ? 'flex-row-reverse' : ''">
    <!-- Avatar -->
    <div
      :class="[
        'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium shrink-0',
        message.role === 'user'
          ? 'bg-blue-600 text-white'
          : 'bg-gray-700 text-white',
      ]"
    >
      {{ message.role === "user" ? "U" : "AI" }}
    </div>

    <!-- Content -->
    <div
      :class="[
        'max-w-[75%] rounded-xl px-4 py-3',
        message.role === 'user'
          ? 'bg-blue-600 text-white'
          : 'bg-gray-100 text-gray-900',
      ]"
    >
      <div
        :class="message.role === 'user' ? 'text-white' : 'prose prose-sm max-w-none'"
        v-html="renderMarkdown(message.content)"
      />

      <!-- Citations -->
      <div
        v-if="message.citations && message.citations.length > 0"
        class="mt-3 pt-3 border-t border-gray-300/30"
      >
        <p class="text-xs font-medium mb-1 opacity-70">Sources:</p>
        <ol class="text-xs space-y-1 opacity-70">
          <li v-for="(cite, i) in message.citations" :key="i">
            <a
              v-if="cite.url"
              :href="cite.url"
              target="_blank"
              rel="noopener"
              class="underline hover:opacity-100"
            >
              {{ cite.title || cite.url }}
            </a>
            <span v-else>{{ cite.title || `Source ${i + 1}` }}</span>
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>
