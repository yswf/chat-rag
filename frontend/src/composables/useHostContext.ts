import { ref, onMounted, onUnmounted, type Ref } from "vue";
import type { HostContext } from "../types";

const ALLOWED_ORIGINS: string[] = ["*"]; // Configure allowed parent origins

function isValidOrigin(origin: string): boolean {
  if (ALLOWED_ORIGINS.includes("*")) return true;
  return ALLOWED_ORIGINS.includes(origin);
}

export function useHostContext(): {
  context: Ref<HostContext | null>;
  isEmbedded: Ref<boolean>;
} {
  const context = ref<HostContext | null>(null);
  const isEmbedded = ref(false);

  function handleMessage(event: MessageEvent): void {
    if (!isValidOrigin(event.origin)) return;

    if (event.data?.type === "CONTEXT_UPDATE") {
      context.value = {
        url: event.data.url || "",
        title: event.data.title || "",
        content: event.data.content || "",
      };
      isEmbedded.value = true;
    }
  }

  onMounted(() => {
    // Check if we are in an iframe
    if (window.self !== window.top) {
      isEmbedded.value = true;
    }
    window.addEventListener("message", handleMessage);
  });

  onUnmounted(() => {
    window.removeEventListener("message", handleMessage);
  });

  return { context, isEmbedded };
}
