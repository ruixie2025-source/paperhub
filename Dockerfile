# syntax=docker/dockerfile:1.7

FROM node:22-alpine AS frontend-build

WORKDIR /build/frontend
ARG NPM_REGISTRY=https://registry.npmmirror.com
COPY frontend/package.json frontend/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --registry="${NPM_REGISTRY}"
COPY frontend/ ./
RUN npm run build


FROM nginx:1.27-alpine AS frontend

COPY deploy/frontend.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /build/frontend/dist /usr/share/nginx/html
EXPOSE 8080


FROM python:3.11-slim-bookworm AS backend

ARG PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple
ARG PYTORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
ARG TORCH_VERSION=2.8.0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    HOME=/tmp

WORKDIR /app
RUN addgroup --system --gid 10001 paperhub \
    && adduser --system --uid 10001 --ingroup paperhub paperhub

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install \
        --index-url "${PYTORCH_INDEX_URL}" \
        --retries 5 \
        "torch==${TORCH_VERSION}"

COPY backend/requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install \
        --index-url "${PIP_INDEX_URL}" \
        --prefer-binary \
        --retries 5 \
        --requirement requirements.txt

COPY backend/app ./app
RUN mkdir -p /data/uploads /data/chroma /models /logs \
    && chown -R paperhub:paperhub /app /data /models /logs

USER paperhub
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*", "--no-access-log"]
