FROM node:22-alpine AS frontend-build

WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


FROM nginx:1.27-alpine AS frontend

COPY deploy/frontend.conf /etc/nginx/conf.d/default.conf
COPY --from=frontend-build /build/frontend/dist /usr/share/nginx/html
EXPOSE 8080


FROM python:3.11-slim-bookworm AS backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HOME=/tmp

WORKDIR /app
RUN addgroup --system --gid 10001 paperhub \
    && adduser --system --uid 10001 --ingroup paperhub paperhub

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --requirement requirements.txt

COPY backend/app ./app
RUN mkdir -p /data/uploads /data/chroma /models /logs \
    && chown -R paperhub:paperhub /app /data /models /logs

USER paperhub
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*", "--no-access-log"]
