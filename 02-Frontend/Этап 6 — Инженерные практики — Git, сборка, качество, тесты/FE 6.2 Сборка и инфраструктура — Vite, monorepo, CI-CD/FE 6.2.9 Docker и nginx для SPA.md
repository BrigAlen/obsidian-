---
type: topic
domain: frontend
stage: 6
section: "6.2"
order: 9
status: todo
level: middle
notion_id: 3ea33104867981fe938fc211e813641e
tags: [domain/frontend, stage/6, level/middle, topic/docker, topic/nginx, topic/spa, topic/deploy, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# Docker и nginx для SPA

↑ [[FE 6.2 Сборка и инфраструктура — Vite, monorepo, CI-CD|6.2 Сборка и инфраструктура: Vite, monorepo, CI/CD]] · ← [[FE 6.2.8 CI-CD для фронтенда|Предыдущая]] · → [[FE 6.2.10 Релиз SPA — runtime config, source maps, CDN-кэш и rollback|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Как упаковать и раздать SPA: multi-stage Dockerfile, history fallback, кэш и безопасность.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build                                    # результат: /app/dist

FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime   # не root, порт 8080
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.d/40-runtime-config.sh /docker-entrypoint.d/    # генерация config.json из env при старте
EXPOSE 8080
HEALTHCHECK CMD wget -qO- http://localhost:8080/healthz || exit 1
```

```nginx
server {
  listen 8080;
  root /usr/share/nginx/html;
  index index.html;

  gzip on; gzip_types text/css application/javascript application/json image/svg+xml;   # или brotli
  add_header X-Content-Type-Options nosniff always;
  add_header X-Frame-Options DENY always;                                      # либо CSP frame-ancestors
  add_header Referrer-Policy strict-origin-when-cross-origin always;
  add_header Content-Security-Policy "default-src 'self'; script-src 'self'; connect-src 'self' https://api.example.com; img-src 'self' data:; style-src 'self' 'unsafe-inline'" always;

  location = /healthz { access_log off; return 200 "ok"; }

  # хэшированные ассеты — кэш на год
  location /assets/ { expires 1y; add_header Cache-Control "public, immutable"; try_files $uri =404; }

  # index.html и runtime-config — не кэшировать
  location = /index.html { add_header Cache-Control "no-cache"; }
  location = /config.json { add_header Cache-Control "no-store"; }

  # history fallback для SPA-маршрутов
  location / { try_files $uri $uri/ /index.html; }

  # проксирование API (одно origin, без CORS)
  location /api/ { proxy_pass http://backend:5000/; proxy_set_header Host $host; proxy_set_header X-Forwarded-For $remote_addr; proxy_read_timeout 60s; }
}
```

Практики:

- Multi-stage: в итоговом образе только статические файлы и nginx (десятки МБ).
- `.dockerignore` (`node_modules`, `dist`, `.git`).
- Не root, минимальный образ, сканирование уязвимостей.
- Кэш: `immutable` для хэшированных файлов, `no-cache` для `index.html`.
- Сжатие Brotli/gzip; HTTP/2.
- SPA fallback: все неизвестные пути → `index.html`; но не для несуществующих ассетов (404).
- Безопасные заголовки (CSP, HSTS на уровне ingress).
- Проксирование `/api` на бэкенд устраняет CORS и скрывает адреса.
- Health endpoint для оркестратора.
- Ingress/CDN перед контейнером в проде.

## Нюансы и подводные камни

- `try_files $uri /index.html` для `/assets/missing.js` отдаёт HTML вместо 404 → «Unexpected token <».
- Кэширование `index.html` приводит к тому, что пользователи не получают новую версию.
- Строгий CSP ломает inline-скрипты/стили (`nonce`/хэши).
- Сборка образа отдельно для каждого окружения — нарушение «один артефакт».
- Размер контекста сборки без `.dockerignore`.

## Практика

1. Соберите образ и запустите SPA, проверив прямой заход на вложенный маршрут.
2. Проверьте заголовки кэширования в DevTools.
3. Настройте CSP без `unsafe-inline` для скриптов.

## Вопросы с ответами

> [!question]- Зачем `try_files ... /index.html`?
> Чтобы клиентские маршруты (History API) при прямом заходе получали `index.html`, а не 404.

> [!question]- Как кэшировать статические файлы SPA?
> Ассеты с хэшем — надолго (`immutable`), `index.html` и runtime-конфиг — без кэша.

## Связанные темы

- [[N:3ea33104867981149d11e5185d139a9b]]
- [[N:71baa0cafa97476da6dc9a5a3b7bb970]]
