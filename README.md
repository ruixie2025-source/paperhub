# PaperHub

PaperHub 是一个面向论文管理、PDF 解析、结构化研究分析和语义问答的本地优先应用。

## 当前能力

- PDF 一键导入、在线阅读和元数据提取
- 论文新增、编辑、删除和关键词搜索
- 研究目的、方法、变量关系和核心发现的结构化分析
- ChromaDB 语义索引与 DeepSeek 论文问答
- SQLite、上传文件和向量索引本地持久化

## 本地启动

后端使用 Python 虚拟环境：

```bash
cd backend
source .venv/bin/activate
export AI_PROVIDER=deepseek
export DEEPSEEK_API_KEY="你的 API Key"
export DEEPSEEK_MODEL="deepseek-v4-flash"
uvicorn app.main:app --reload
```

前端使用 Vite：

```bash
cd frontend
npm install
npm run dev
```

打开 `http://127.0.0.1:5173`。后端健康检查位于 `http://127.0.0.1:8000/health`。

## 本地数据

- SQLite：`backend/paperhub.db`
- PDF 文件：`backend/uploads/`
- ChromaDB：`backend/chroma/`

部署时必须持久化这三个位置，并定期备份。不要把 DeepSeek API Key 写入代码或提交到 Git。

## 部署提醒

- 公网开放前使用 Nginx Basic Auth 或其他登录方案限制访问。
- 使用 HTTPS，并限制上传体积和请求超时时间。
- React Router 需要将前端未知路径回退到 `index.html`。
- 当前 Embedding 模型为 `BAAI/bge-m3`；若保持该模型，建议使用至少 4 核 8G 的服务器。
- 生产环境不要使用 Vite 开发服务器或 `uvicorn --reload`。
