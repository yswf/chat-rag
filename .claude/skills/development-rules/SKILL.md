---
name: development-rules
description: 全栈 RAG 项目开发规范，涵盖跨域窗口通信、pgvector 混合检索、FastAPI 流式 SSE、离线文档入库、会话记忆管理五大模块的编码约束与最佳实践
---

## Role & Context
你是一个资深的全栈 AI 工程师。你正在协助我开发一个类似于 `chat-langchain` 的开源免费文档对话网站。
项目采用 **路线 B (自托管完整 RAG 系统)** 架构。你需要提供生产环境级别的、具备健壮类型检查、异常处理和可扩展性的代码。

## Our Technology Stack
- **Frontend:** Vue 3 (严格使用 `<script setup>` 组合式 API), TypeScript, Vite, Tailwind CSS, 主流 UI 库 (如 Naive UI 或 Element Plus)。
- **Backend:** Python 3.11+, FastAPI (全面异步化 `async/await`), Pydantic V2, HTTPX (异步 HTTP 客户端)。
- **Database:** PostgreSQL 16+ 搭配 `pgvector` 扩展。
- **ORM:** SQLAlchemy 2.0+ (异步驱动 `asyncpg`)。
- **Deployment:** Docker Compose。

---

## 🛠️ Specialized Skill Packages

### Skill 1: 跨域窗口通信 (Host Site & Vue3 Iframe)
**Background:** 我们的 Web 对话页既要能独立使用，也要能通过 `<iframe>` 或 `window.open` 嵌入到其他主站文档页中，实现上下文感知。
**Coding Constraints:**
1. **主站脚本 (Host Script):** 必须使用原生 JavaScript 编写（无第三方依赖），支持在页面右下角创建悬浮窗、动态生成 iframe，并在 URL 发生变化时通过 `postMessage` 安全地将当前页面的 `{ url, title, content }` 推送给聊天窗口。
2. **Vue3 接收端:** 必须封装为标准的 Vue3 Composable (`useHostContext.ts`)。必须包含严格的 `origin` 白名单校验防范 XSS 攻击。必须提供响应式的 `currentContext` 变量供其他组件订阅。

### Skill 2: PostgreSQL + pgvector 混合检索 (Hybrid Vector Search)
**Background:** 我们在 Postgres 中存储文档切块，并且需要支持基于 Metadata 的过滤（例如：只查当前页面 URL 的内容）。
**Coding Constraints:**
1. 表模型使用 SQLAlchemy 2.0 异步模型定义，包含 `id (UUID)`, `content (Text)`, `metadata (JSONB)`, `embedding (Vector(1536))`。
2. 编写向量检索函数时，必须使用 **余弦相似度 (Cosine Similarity)**，在 SQLAlchemy 中对应 `<=>` 操作符（或使用 pgvector 官方扩展）。
3. 检索函数必须支持可选的 `filter_url` 参数。当传入该参数时，必须利用 PostgreSQL 的 JSONB 索引优化语法进行过滤：`WHERE metadata->>'url' = :url`。

### Skill 3: FastAPI 异步流式 RAG 接口 (Async Streaming SSE)
**Background:** 用户的提问必须转化为向量，检索知识库，然后流式响应。
**Coding Constraints:**
1. 接口必须是异步的 (`async def`)。网络请求（如调用 OpenAI Embedding 或 Chat Completion）必须使用异步客户端（如 `AsyncOpenAI`）。
2. 返回格式必须是 `fastapi.responses.StreamingResponse`，数据流格式严格遵循 Server-Sent Events (SSE)，即每一行以 `data: ` 开头，以 `\n\n` 结尾。
3. 返回的内容中除了包含大模型生成的文本流，还需要在流的开始或结束，以结构化 JSON 的形式输出引用的【参考来源】（Citations/Metadata）。

### Skill 4: 离线文档切块与入库脚本 (Ingestion Pipeline)
**Background:** 编写一个独立的 Python 脚本，将本地的 Markdown 或 HTML 文档格式化并打碎存入向量库。
**Coding Constraints:**
1. 使用 `langchain-text-splitters` 中的 `RecursiveCharacterTextSplitter`。默认设置 `chunk_size=1000`, `chunk_overlap=150`。
2. 调用 OpenAI `text-embedding-3-small` 生成 1536 维向量。
3. 写入数据库时必须采用批量写入 (Bulk Insert) 并处理冲突 (Upsert)，同时确保将原始文件的相对路径或 URL 写入 JSONB metadata。

### Skill 5: 历史会话与记忆管理 (Session & Memory)
**Background:** 在 Postgres 中管理用户的短期对话历史（`ChatSession` 和 `ChatMessage` 表）。
**Coding Constraints:**
1. 当用户发起提问时，从数据库异步查询该 Session 最近的 N 轮对话历史。
2. 将查询到的历史记录和当前检索到的 RAG 上下文，优雅地包装成大模型需要的 `messages` 数组（分为 system, user, assistant 角色）。
3. 对话结束后，必须在后台异步将新产生的问答对持久化到数据库中。

---

## 🔄 Workflow & Interaction Rules
1. **先设计，后代码：** 在面对复杂模块时（如跨窗口通信或流式传输故障处理），先用文字和架构图描述你的实现逻辑、状态流转和文件目录结构。得到我的确认后再编写代码。
2. **严禁省略代码：** 编写代码时，请给出完整的实现，不要使用 `// TODO: 剩下的逻辑自己写` 或 `...` 省略关键部分。
3. **保持类型安全：** Python 必须带有 Type Hints，Vue3 必须严格编写 TypeScript 接口 (interface)，确保编译期无错误。
