# 🚀 RAG Chat Web - 开发任务清单 (Task List)

本项目旨在开发一个开源免费、类似 `chat-langchain` 的文档对话网站，支持独立使用及通过 iframe 嵌入其他网站提供页面级上下文问答。

## 阶段 1：环境基座与数据库设计 (Infrastructure)
目标：搭建底层基础设施，定好数据字典。

- [ ] **Task 1.1: 初始化代码仓库**
  - 建立 `frontend` 和 `backend` 目录。
  - 配置 `.gitignore`。
  - 创建 `.clauderules` 并填入核心技能规范。
- [ ] **Task 1.2: 部署 PostgreSQL + pgvector**
  - 编写基础的 `docker-compose.yml`。
  - 拉取带有 `pgvector` 扩展的 Postgres 镜像（如 `ankane/pgvector`）。
  - 配置端口映射 (5432) 和数据卷本地持久化挂载。
- [ ] **Task 1.3: 数据库连接与 ORM 配置**
  - 在 FastAPI 中引入 `asyncpg` 和 `SQLAlchemy 2.0+`。
  - 建立数据库异步引擎 (AsyncEngine) 和会话生成器 (sessionmaker)。
- [ ] **Task 1.4: 定义核心表结构**
  - 定义 `Document` 表（包含 `content`, `metadata` JSONB, `embedding` Vector）。
  - 定义 `ChatSession` 表（会话主表）。
  - 定义 `ChatMessage` 表（消息流水表，关联 Session）。
  - 编写自动建表脚本或使用 Alembic 初始化数据库。

## 阶段 2：离线数据管道 (Data Ingestion)
目标：编写独立脚本，将本地文档转化为可搜索的向量并入库。

- [ ] **Task 2.1: 文件读取与解析**
  - 编写 Python 脚本，遍历并读取本地测试用的 Markdown/HTML 文档。
- [ ] **Task 2.2: 文本切块 (Chunking)**
  - 引入 LangChain 的 `RecursiveCharacterTextSplitter`。
  - 按照 1000 Token 大小、150 Token 重叠度将长文档切片。
- [ ] **Task 2.3: 向量化处理 (Embedding)**
  - 接入 OpenAI API，调用 `text-embedding-3-small` 接口将文本块转化为 1536 维向量。
- [ ] **Task 2.4: 批量入库与元数据处理**
  - 提取当前文件所属的 URL 或相对路径、标题。
  - 将文本内容、向量数组和构建好的 Metadata (`{"url": "...", "title": "..."}`) 一起批量插入 (Bulk Insert) Postgres。

## 阶段 3：后端核心 API 开发 (FastAPI)
目标：实现基于向量的检索和带记忆的流式对话接口。

- [ ] **Task 3.1: 实现混合检索函数**
  - 编写异步函数，接收用户问题向量。
  - 使用余弦相似度 (`<=>`) 从 Postgres 检索 Top-K 记录。
  - **核心逻辑**：加入对 JSONB 字段的过滤支持（`WHERE metadata->>'url' = :url`）。
- [ ] **Task 3.2: 实现会话记忆逻辑**
  - 编写工具函数，根据前端传来的 `session_id` 查询最近 5-10 条历史消息。
  - 编写后台任务逻辑，在流式对话结束后，将用户提问和 AI 回答异步写入数据库。
- [ ] **Task 3.3: 开发流式对话接口 (`/api/chat`)**
  - 组装检索结果、历史对话、当前问题，构建符合 OpenAI 格式的 Prompt。
  - 使用 `AsyncOpenAI` 客户端发起请求 (`stream=True`)。
  - 使用 FastAPI `StreamingResponse` 返回 Server-Sent Events (SSE) 格式的数据流。

## 阶段 4：前端交互与跨域通信 (Vue3)
目标：实现对话界面以及主站 iframe 的跨域通信。

- [ ] **Task 4.1: Vue3 项目搭建**
  - 使用 Vite 初始化 Vue3 + TS 项目。
  - 引入 Tailwind CSS 和基础 UI 库（Naive UI / Element Plus）。
- [ ] **Task 4.2: 实现跨域通信监听**
  - 编写 `useHostContext.ts` 组合式函数。
  - 监听 `message` 事件，**严格校验 Origin**，提取并保存宿主页面的 URL 和标题。
- [ ] **Task 4.3: 对话 UI 与流式渲染**
  - 构建左侧历史会话侧边栏和主对话区域。
  - 使用 `fetch` 或 `@microsoft/fetch-event-source` 接收并解析后端 SSE 流，实现打字机效果。
- [ ] **Task 4.4: Markdown 渲染与引用展示**
  - 引入 `markdown-it` 和代码高亮库实时渲染 AI 回答。
  - 解析后端返回的参考来源 (Citations)，在气泡底部渲染可点击的引用链接。
- [ ] **Task 4.5: 编写主站原生 JS 注入脚本**
  - 编写一段无任何依赖的原生 JS。
  - 实现在页面右下角生成悬浮按钮，点击后展开 `iframe`。
  - 监听前端路由变化，并通过 `postMessage` 向 iframe 推送当前页面的 Context。

## 阶段 5：容器化打包与开源发布 (Deployment)
目标：确保项目能一键拉起，具备开源推广的条件。

- [ ] **Task 5.1: 编写前端 Dockerfile**
  - 采用多阶段构建，第一阶段使用 Node 构建产物，第二阶段使用 Nginx 托管静态文件。
- [ ] **Task 5.2: 编写后端 Dockerfile**
  - 基于 Python 3.11 镜像，安装所需依赖，使用 Uvicorn 启动 FastAPI 服务。
- [ ] **Task 5.3: 完善全局 docker-compose.yml**
  - 将前端、后端、数据库编排在同一个内部网络。
  - 统一配置 `.env` 环境变量文件模板（包含 OpenAI API Key、数据库密码等）。
- [ ] **Task 5.4: 完善文档与开源说明**
  - 撰写 `README.md`，重点说明如何执行 `docker-compose up -d`。
  - 补充“如何将此 Chatbot 嵌入到你自己的网站”的使用教程（包含原生 JS 脚本引入说明）。