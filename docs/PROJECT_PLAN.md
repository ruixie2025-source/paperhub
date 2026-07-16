# PaperHub Project Plan

## 1. 项目简介

PaperHub 是一个用于学习 Codex 协作开发流程的论文管理项目。项目已从本地 MVP 进入 v1.0 生产化阶段，并保留简单、清晰、可迭代的架构。

项目当前已经完成 PDF 解析、结构化分析、向量检索和 RAG 问答，并使用 Docker Compose、Nginx Basic Auth、限流和持久化卷支持单机公网部署。

## 2. 第一阶段目标

第一阶段目标是完成本地最小可用版本，也就是 MVP。

- 建立清晰的前后端分离项目结构。
- 使用 FastAPI 提供本地 API 服务。
- 使用 SQLite 存储论文数据。
- 使用 SQLAlchemy 管理数据库模型和读写逻辑。
- 使用 React + Vite + TypeScript 构建前端页面。
- 使用 TailwindCSS + shadcn/ui 构建基础 UI。
- 完成论文的新增、查看、编辑、删除和基础搜索。
- 使用 FastAPI 自动生成的 OpenAPI 文档辅助接口调试。
- 通过本文件维护项目计划和开发进度。

## 3. 第二阶段目标

第二阶段目标是增强论文管理与阅读体验。

- 增加标签和分类能力。
- 增加阅读状态，例如待读、阅读中、已读、重点。
- 增加论文笔记和摘录。
- 优化搜索和筛选体验。
- 增加基础统计，例如论文数量、年份分布、标签分布。
- 完善错误处理、空状态、加载状态和表单校验。
- 补充必要的测试和开发脚本。

## 4. 第三阶段目标

第三阶段目标是完成 AI、RAG 和生产部署基础。

- 接入 OpenAlex、Crossref 等论文 API。
- 支持从外部 API 导入论文元数据。
- 完成 AI 元数据、结构化论文分析和研究问题提取。
- 完成 ChromaDB、语义检索和 RAG 问答。
- 使用 Docker Compose 统一生产运行环境。
- 使用 Nginx 提供反向代理、Basic Auth、静态缓存和 HTTPS 接入位置。
- 增加限流、统一日志、异常脱敏、处理超时和依赖健康检查。

## 5. 技术栈

第一阶段采用简单、稳定、适合本地学习的技术栈。

- 前端框架：React + Vite + TypeScript
- 前端样式：TailwindCSS
- UI 组件：shadcn/ui
- 后端框架：FastAPI
- AI Provider：DeepSeek
- 数据校验：Pydantic
- ORM：SQLAlchemy
- 数据库：SQLite
- 向量数据库：ChromaDB
- Embedding：SentenceTransformers + BAAI/bge-m3
- API 文档：FastAPI 自动生成 OpenAPI、Swagger UI、ReDoc
- 生产运行：Docker Compose + Nginx

当前保持设计状态、暂不实现：

- PostgreSQL
- Redis
- pgvector
- JWT 用户系统
- Celery 后台任务
- 对象存储

## 6. 项目目录说明

- `README.md`：项目入口说明，记录项目用途、启动方式和基本开发说明。
- `AGENTS.md`：Codex 和其他 AI coding agent 的协作说明。
- `.gitignore`：Git 忽略规则。
- `docs/`：项目文档目录。本项目唯一开发计划文档是 `docs/PROJECT_PLAN.md`。
- `backend/`：后端项目目录，后续放置 FastAPI 应用、API 路由、数据模型、数据库访问逻辑等。
- `frontend/`：前端项目目录，后续放置 React + Vite + TypeScript 应用、页面、组件和样式。
- `database/`：数据库相关目录，后续放置 SQLite 数据库说明、迁移记录或初始化资料。
- `scripts/`：项目辅助脚本目录，后续放置本地启动、检查、初始化等脚本。
- `deploy/`：生产 Nginx 网关和前端静态服务配置。
- `Dockerfile`：前端构建、前端运行和后端运行的多阶段生产镜像。
- `docker-compose.yml`：编排 frontend、backend、nginx、健康检查、日志和持久化卷。
- `.env.example`：不含真实密钥的统一环境变量模板。

## 7. MVP（第一版）功能列表

第一版只做论文管理的最小闭环。

- 论文列表页
- 新增论文
- 查看论文详情
- 编辑论文
- 删除论文
- 基础搜索
- SQLite 本地持久化
- FastAPI API 文档
- 前端调用后端 API
- 基础错误提示和空状态

## 8. 后续迭代计划

后续迭代按照“先可用，再好用，再智能”的顺序推进。

1. 完成本地 MVP。
2. 增加标签、分类、阅读状态和笔记。
3. 优化前端交互体验和视觉一致性。
4. 增加基础统计和筛选能力。
5. 接入 OpenAlex、Crossref 等论文 API。
6. 增加 AI 摘要和结构化提取。
7. 从普通搜索升级到 RAG。
8. 完成 Docker、Nginx 和单机生产加固。
9. 配置正式域名、HTTPS 证书、备份和监控。
10. 在数据量和用户量增长后执行 PostgreSQL 等架构升级。

未来架构只做以下设计，不在 v1.0 实现：

- 登录与用户系统：JWT 短期访问令牌、可轮换刷新令牌、Argon2id 密码哈希、角色权限和服务端撤销机制。
- 数据库：SQLite 通过 Alembic 迁移到 PostgreSQL，先建立可重复迁移和备份恢复演练，再切换生产数据。
- 缓存与限流：Redis 保存多实例共享的限流计数、短期缓存和会话撤销状态。
- 后台任务：Celery 处理 PDF 解析、Embedding、索引重建和长耗时 AI 分析，API 返回任务状态而不是长期占用请求。
- 文件存储：PDF 迁移到兼容 S3 的对象存储，使用短期签名 URL 和服务端文件策略。
- 向量检索：数据量需要统一事务和检索基础设施时，将 ChromaDB 迁移到 PostgreSQL + pgvector。

## 9. 当前开发进度（Todo Checklist）

以后每完成一个功能，都需要同步更新本 Checklist。

- [x] 初始化基础项目目录。
- [x] 确定第一阶段技术方案。
- [x] 创建唯一开发计划文档 `docs/PROJECT_PLAN.md`。
- [x] 初始化后端 FastAPI 项目结构。
- [x] 初始化前端 React + Vite + TypeScript 项目结构。
- [x] 配置 TailwindCSS。
- [x] 配置 shadcn/ui。
- [x] 设计第一版论文数据模型。
- [x] 配置 SQLite 与 SQLAlchemy。
- [x] 初始化 SQLite 数据库并创建第一版数据表。
- [x] 实现 Paper Service CRUD。
- [x] 实现论文新增接口。
- [x] 实现论文列表接口。
- [x] 实现论文详情接口。
- [x] 实现论文编辑接口。
- [x] 实现论文删除接口。
- [x] 实现基础搜索接口。
- [x] 实现论文列表页面。
- [x] 实现新增论文页面或表单。
- [x] 实现论文详情页面。
- [x] 实现 PDF 上传和静态文件访问。
- [x] 实现 PDF 一键导入论文。
- [x] 实现 PDF 在线阅读。
- [x] 实现 PDF 文本解析并保存全文。
- [x] 实现 AI 元数据自动提取并写入空字段。
- [x] 实现论文文本固定长度切块方法。
- [x] 实现论文文本 Embedding 向量生成方法。
- [x] 实现 ChromaDB 向量数据库。
- [x] 实现 Semantic Retrieval。
- [x] 实现 RAG QA。
- [x] 实现论文结构化分析表格。
- [x] 实现论文结构化分析记录保存与清理。
- [x] 完成部署前接口与持久化路径检查。
- [x] 修复分析记录代理和 AI 问答页面路由冲突。
- [x] 增加 PDF 文件大小、类型和文件头校验。
- [x] 实现删除论文和替换 PDF 时的文件、分析记录与向量索引清理。
- [x] 完成论文库、AI 问答和详情页响应式 UI 升级。
- [x] 修复移动端 PDF 阅读器横向溢出。
- [x] 使用 Nginx Basic Auth 保护全站，仅开放匿名健康检查。
- [x] 为上传、聊天和论文分析增加 FastAPI 限流。
- [x] 使用统一环境变量配置数据库、上传、向量库、模型缓存和 AI 服务。
- [x] 实现 DeepSeek 错误日志、重试和客户端错误脱敏。
- [x] 增加 Dockerfile、Docker Compose 和 Nginx 生产配置。
- [x] 增加统一访问日志、错误日志、AI 日志和上传日志。
- [x] 增加全局异常处理、PDF 解析超时与失败重试。
- [x] 扩展健康检查到 SQLite、ChromaDB 和 DeepSeek 配置状态。
- [x] 增加 `.env.example`、生产部署文档、MIT License 和完整忽略规则。
- [ ] 为正式域名配置 HTTPS 证书并验证自动续期。
- [ ] 完成云服务器部署与生产环境验证。
- [x] 实现编辑论文页面或表单。
- [x] 前端接入后端 API。
- [x] 重构前端组件结构和 Paper Hook。
- [x] 完成本地 MVP 验证。
