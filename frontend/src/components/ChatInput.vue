<script setup lang="ts">
import { ref } from "vue";

const emit = defineEmits<{
  send: [content: string];
}>();

defineProps<{
  isStreaming: boolean;
}>();

const input = ref("");

function handleSubmit(): void {
  if (!input.value.trim()) return;
  emit("send", input.value.trim());
  input.value = "";
}
</script>

<template>
  <div class="border-t bg-white p-4">
    <form
      class="flex gap-3 max-w-4xl mx-auto"
      @submit.prevent="handleSubmit"
    >
      <input
        v-model="input"
        type="text"
        placeholder="Ask a question about the documentation..."
        class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
        :disabled="isStreaming"
        autofocus
      />
      <button
        type="submit"
        :disabled="isStreaming || !input.trim()"
        class="px-5 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-xl text-sm font-medium transition-colors"
      >
        <template v-if="isStreaming">⏳</template>
        <template v-else>Send</template>
      </button>
    </form>
  </div>
</template>
