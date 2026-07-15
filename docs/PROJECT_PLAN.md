# PaperHub Project Plan

## 1. 项目简介

PaperHub 是一个用于学习 Codex 协作开发流程的本地论文管理项目。第一阶段重点不是追求复杂架构，而是通过一个清晰、可运行、可迭代的项目，学习如何让 Codex 参与项目规划、文件组织、功能开发、调试和进度维护。

项目初期只面向本地开发，核心目标是完成论文条目的基础管理。项目成熟后，再逐步升级到 PostgreSQL、Docker、RAG、AI 摘要和外部论文 API 集成。

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

第二阶段目标是增强论文管理体验，让项目更接近真实使用场景。

- 增加标签和分类能力。
- 增加阅读状态，例如待读、阅读中、已读、重点。
- 增加论文笔记和摘录。
- 优化搜索和筛选体验。
- 增加基础统计，例如论文数量、年份分布、标签分布。
- 完善错误处理、空状态、加载状态和表单校验。
- 补充必要的测试和开发脚本。

## 4. 第三阶段目标

第三阶段目标是为 AI、RAG 和外部论文数据源做准备。

- 接入 OpenAlex、Crossref 等论文 API。
- 支持从外部 API 导入论文元数据。
- 增加 AI 摘要、关键词提取和研究问题提取能力。
- 从普通关键词搜索逐步升级到 RAG 检索。
- 在项目成熟后，将 SQLite 迁移到 PostgreSQL。
- 在项目成熟后，引入 Docker 统一本地和部署环境。
- 在需要部署时，再规划云服务器、反向代理和生产环境配置。

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
- API 文档：FastAPI 自动生成 OpenAPI、Swagger UI、ReDoc
- 运行方式：本地开发运行

第一阶段最初暂不考虑、目前已随项目成熟逐步引入：

- Docker
- PostgreSQL
- 云服务器
- Redis
- pgvector
- RAG（已完成本地版本）

## 6. 项目目录说明

- `README.md`：项目入口说明，记录项目用途、启动方式和基本开发说明。
- `AGENTS.md`：Codex 和其他 AI coding agent 的协作说明。
- `.gitignore`：Git 忽略规则。
- `docs/`：项目文档目录。本项目唯一开发计划文档是 `docs/PROJECT_PLAN.md`。
- `backend/`：后端项目目录，后续放置 FastAPI 应用、API 路由、数据模型、数据库访问逻辑等。
- `frontend/`：前端项目目录，后续放置 React + Vite + TypeScript 应用、页面、组件和样式。
- `database/`：数据库相关目录，后续放置 SQLite 数据库说明、迁移记录或初始化资料。
- `scripts/`：项目辅助脚本目录，后续放置本地启动、检查、初始化等脚本。

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
8. 将 SQLite 迁移到 PostgreSQL。
9. 引入 Docker。
10. 规划云服务器部署。

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
- [ ] 为公网部署配置访问保护和 HTTPS。
- [ ] 完成云服务器部署与生产环境验证。
- [x] 实现编辑论文页面或表单。
- [x] 前端接入后端 API。
- [x] 重构前端组件结构和 Paper Hook。
- [x] 完成本地 MVP 验证。
