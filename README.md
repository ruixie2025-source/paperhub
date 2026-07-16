# PaperHub

PaperHub 是一个用于论文管理、PDF 解析、结构化研究分析和语义问答的全栈应用。当前版本使用 React、FastAPI、SQLite、ChromaDB、BGE-M3 和 DeepSeek。

## 功能

- PDF 一键导入、在线阅读和元数据提取
- 论文新增、编辑、删除和关键词搜索
- 研究目的、方法、变量关系和核心发现的结构化分析
- ChromaDB 语义索引与 DeepSeek 论文问答
- SQLite、PDF 文件和向量索引持久化

## 环境要求

- 本地开发：Python 3.11、Node.js 22、npm 10
- 生产部署：Docker Engine 与 Docker Compose v2
- Embedding 模型首次运行需要下载；建议服务器至少 4 核 CPU、8 GB 内存和 20 GB 可用磁盘

## 环境变量

不要修改源码填写 API Key。正确流程是复制环境变量模板，生成被 Git
忽略的本地 `.env`，再在 `.env` 中填写自己的配置：

```bash
cp .env.example .env
```

`.env.example` 只保存变量名称，所有赋值均为空。复制后请在 `.env`
中填写所需值；可选配置如果希望使用代码中的默认值，可以从 `.env`
删除对应空行。最小本地配置示例：

```dotenv
APP_ENVIRONMENT=development
LOG_LEVEL=INFO
DATABASE_PATH=backend/paperhub.db
UPLOAD_DIR=backend/uploads
CHROMA_DIR=backend/chroma
MODEL_CACHE_DIR=backend/model-cache
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
VITE_DEV_API_TARGET=http://127.0.0.1:8000
```

必须检查的生产配置：

- `DEEPSEEK_API_KEY`：DeepSeek API Key，不得提交到 Git
- `ALLOWED_HOSTS`：增加正式域名或服务器公网 IP
- `TRUST_PROXY_HEADERS=true`：仅在后端只允许受信任 Nginx 访问时启用
- `DATABASE_PATH`、`UPLOAD_DIR`、`CHROMA_DIR`：Compose 已覆盖到持久化卷
- `UPLOAD_RATE_LIMIT`、`CHAT_RATE_LIMIT`、`ANALYSIS_RATE_LIMIT`：接口频率限制

## 本地开发

后端：

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
npm ci
npm run dev
```

打开 `http://127.0.0.1:5173`。本地后端为 `http://127.0.0.1:8000`，健康检查为 `GET /health`。Vite 从项目根目录 `.env` 读取开发代理地址。

## Docker 生产部署

1. 复制并编辑 `.env`，将 `APP_ENVIRONMENT` 改为 `production`，填写 DeepSeek Key 和正式 `ALLOWED_HOSTS`。
2. 创建 Basic Auth 密码文件：

```bash
mkdir -p secrets
docker run --rm -it httpd:2.4-alpine htpasswd -nB paperhub > secrets/nginx.htpasswd
chmod 600 secrets/nginx.htpasswd
```

命令会交互式要求输入密码，明文密码不会写入源码、`.env`、Shell
历史或 `docker-compose.yml`。生成的哈希文件位于被 Git 忽略的
`secrets/` 目录，并通过 Docker secret 只读挂载到 Nginx。

3. 校验并启动：

```bash
docker compose config
docker compose up -d --build
docker compose ps
curl http://127.0.0.1/health
```

Nginx 是唯一暴露端口的服务。全站、API、上传文件和 API 文档都受 Basic Auth 保护，只有 `/health` 可匿名访问。SQLite、上传文件、ChromaDB、模型缓存和后端日志保存在 Docker named volumes 中。

## HTTPS

HTTP Basic Auth 必须与 HTTPS 一起用于公网，否则用户名和密码可能被截获。`deploy/nginx/default.conf` 已保留 TLS 配置位置；正式开放前应完成以下任一方案：

- 在阿里云 ALB/SLB 上安装证书并终止 TLS，只允许负载均衡器访问服务器 80 端口。
- 使用 Certbot 获取证书，为 Nginx 增加 `listen 443 ssl`，挂载证书，并将 80 端口重定向到 HTTPS。

完成证书配置前，不要把当前 HTTP 端口直接开放给公网。

## 运维

- 查看状态：`docker compose ps`
- 查看日志：`docker compose logs -f --tail=200`
- 更新服务：`docker compose up -d --build`
- 停止服务：`docker compose down`
- 不要使用 `docker compose down -v`，该命令会删除持久化数据卷
- 定期备份 `paperhub-data` 卷；SQLite、PDF 与 Chroma 索引应作为同一恢复点保存
- DeepSeek 健康检查默认只检查 Key 是否配置；启用 `HEALTHCHECK_DEEPSEEK_NETWORK=true` 后会检查网络连通性，但不会发起付费模型请求

## 安全说明

- 不要把 `.env`、密码文件、数据库、PDF、Chroma 数据或模型缓存提交到 Git
- 后端和前端容器不发布宿主机端口，避免绕过 Nginx 认证
- 上传限制默认为 50 MB；Nginx 与 FastAPI 两侧同时限制
- 上传、问答和论文分析均有限流；当前单实例使用内存计数，多实例部署时应改用 Redis
- AI 服务端会记录完整上游错误，客户端只返回统一的临时不可用提示

## API 文档

运行后访问 `/docs` 或 `/redoc`。生产环境中这些路径同样需要 Basic Auth。

## License

[MIT](LICENSE)
