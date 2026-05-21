<script setup lang="ts">
import type { ChatSession } from "../types";

defineProps<{
  sessions: ChatSession[];
  currentSessionId: string | null;
}>();

const emit = defineEmits<{
  select: [id: string];
  new: [];
  delete: [id: string];
}>();
</script>

<template>
  <aside
    class="w-64 bg-gray-900 text-gray-200 flex flex-col shrink-0"
  >
    <div class="p-4 border-b border-gray-700">
      <h1 class="text-lg font-semibold text-white">ChatRAG</h1>
      <button
        class="mt-3 w-full py-2 px-3 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
        @click="emit('new')"
      >
        + New Chat
      </button>
    </div>

    <div class="flex-1 overflow-y-auto py-2">
      <div v-if="sessions.length === 0" class="px-4 py-2 text-sm text-gray-500">
        No conversations yet
      </div>
      <div
        v-for="session in sessions"
        :key="session.id"
        :class="[
          'group flex items-center gap-2 px-4 py-2.5 mx-2 rounded-lg cursor-pointer text-sm transition-colors',
          session.id === currentSessionId
            ? 'bg-gray-700 text-white'
            : 'hover:bg-gray-800 text-gray-400',
        ]"
        @click="emit('select', session.id)"
      >
        <span class="truncate flex-1">{{ session.title }}</span>
        <button
          class="hidden group-hover:block text-gray-500 hover:text-red-400 text-xs shrink-0"
          @click.stop="emit('delete', session.id)"
        >
          ✕
        </button>
      </div>
    </div>
  </aside>
</template>
