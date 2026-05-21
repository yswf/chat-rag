/**
 * ChatRAG Embed Script
 *
 * Adds a floating chat button to the bottom-right corner of any webpage.
 * Clicking it opens an iframe with the ChatRAG chat interface.
 * Automatically sends page context (URL, title, content) via postMessage.
 *
 * Usage:
 *   <script src="https://your-domain.com/chatrag-embed.js" defer></script>
 */
(function () {
  "use strict";

  var CHAT_URL = "http://localhost:5173";
  var BUTTON_TEXT = "💬 Chat";
  var IFRAME_WIDTH = "420px";
  var IFRAME_HEIGHT = "600px";

  // --- Do not edit below ---
  var button = null;
  var iframeContainer = null;
  var iframe = null;
  var isOpen = false;

  function createButton() {
    button = document.createElement("button");
    button.textContent = BUTTON_TEXT;
    button.style.cssText =
      "position:fixed;bottom:20px;right:20px;z-index:9999;" +
      "padding:12px 20px;background:#2563eb;color:#fff;border:none;" +
      "border-radius:9999px;font-size:14px;font-weight:600;cursor:pointer;" +
      "box-shadow:0 4px 12px rgba(37,99,235,0.4);transition:transform 0.2s;";
    button.onmouseenter = function () {
      button.style.transform = "scale(1.05)";
    };
    button.onmouseleave = function () {
      button.style.transform = "scale(1)";
    };
    button.onclick = toggleChat;
    document.body.appendChild(button);
  }

  function createIframe() {
    iframeContainer = document.createElement("div");
    iframeContainer.style.cssText =
      "position:fixed;bottom:80px;right:20px;z-index:9998;" +
      "width:" +
      IFRAME_WIDTH +
      ";height:" +
      IFRAME_HEIGHT +
      ";" +
      "border-radius:12px;overflow:hidden;display:none;" +
      "box-shadow:0 8px 40px rgba(0,0,0,0.15);" +
      "background:#fff;";

    var toolbar = document.createElement("div");
    toolbar.style.cssText =
      "display:flex;justify-content:flex-end;padding:6px 10px;background:#f8f9fa;border-bottom:1px solid #e5e7eb;";
    var closeBtn = document.createElement("button");
    closeBtn.textContent = "✕";
    closeBtn.style.cssText =
      "background:none;border:none;font-size:18px;cursor:pointer;color:#6b7280;padding:2px 6px;";
    closeBtn.onclick = toggleChat;
    toolbar.appendChild(closeBtn);

    iframe = document.createElement("iframe");
    iframe.src = CHAT_URL;
    iframe.style.cssText =
      "width:100%;height:calc(100% - 36px);border:none;";
    iframe.allow = "clipboard-write";

    iframeContainer.appendChild(toolbar);
    iframeContainer.appendChild(iframe);
    document.body.appendChild(iframeContainer);
  }

  function getPageContext() {
    var content = "";
    var article = document.querySelector("article");
    if (article) {
      content = article.textContent || "";
      content = content.substring(0, 3000);
    }
    return {
      type: "CONTEXT_UPDATE",
      url: window.location.href,
      title: document.title,
      content: content,
    };
  }

  function sendContext() {
    if (iframe && iframe.contentWindow) {
      iframe.contentWindow.postMessage(getPageContext(), CHAT_URL);
    }
  }

  function toggleChat() {
    isOpen = !isOpen;
    iframeContainer.style.display = isOpen ? "block" : "none";
    if (isOpen) {
      // Wait for iframe to load, then send context
      setTimeout(sendContext, 500);
    }
  }

  // Initialize
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    createButton();
    createIframe();

    iframe.addEventListener("load", function () {
      sendContext();
    });

    // Watch for URL changes (SPA navigation)
    var lastUrl = window.location.href;
    new MutationObserver(function () {
      var currentUrl = window.location.href;
      if (currentUrl !== lastUrl) {
        lastUrl = currentUrl;
        sendContext();
      }
    }).observe(document, { subtree: true, childList: true });

    // Also handle popstate for SPA routers
    window.addEventListener("popstate", function () {
      setTimeout(function () {
        if (window.location.href !== lastUrl) {
          lastUrl = window.location.href;
          sendContext();
        }
      }, 100);
    });
  }
})();
