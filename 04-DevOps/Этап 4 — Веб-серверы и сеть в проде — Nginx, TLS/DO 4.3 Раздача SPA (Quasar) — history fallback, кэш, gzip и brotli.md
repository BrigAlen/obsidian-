---
type: topic
domain: devops
stage: 4
order: 3
status: todo
level: middle
tags: [domain/devops, stage/4, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 7
---

# Раздача SPA (Quasar): history fallback, кэш, gzip и brotli

↑ [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Развёртывание Vue/Quasar-приложения: fallback на index.html, кэширование, сжатие, runtime-конфигурация.

## history fallback

SPA с `createWebHistory()` использует «чистые» URL (`/orders/42`). При обновлении страницы браузер запрашивает этот путь у сервера; файла нет → 404. Нужно отдавать `index.html` для всех путей, которые не являются файлами.

```nginx
server {
    listen 8080;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;          # файл → каталог → fallback
    }

    # API не должен отдавать index.html при 404
    location /api/ { proxy_pass http://api:8080/; }
}
```

Проверка: `curl -I https://app/orders/42` → 200 и HTML. Для статических ассетов несуществующий файл (`/assets/missing.js`) лучше отдавать 404, а не `index.html` (иначе ошибка MIME): отдельный `location /assets/ { try_files $uri =404; }`.

## Кэширование

Схема (Vite/Quasar создают имена с **хэшем содержимого**):

| Ресурс | Заголовок |
|---|---|
| `index.html` | `Cache-Control: no-cache` (проверять каждый раз; с ETag → 304) |
| `/assets/*` (хэшированные js/css/шрифты/картинки) | `public, max-age=31536000, immutable` |
| `config.json` (runtime-конфигурация) | `no-store` |
| `favicon`, `manifest`, `sw.js` | `no-cache` (service worker обязательно) |

```nginx
location = /index.html { add_header Cache-Control "no-cache" always; }
location = /config.json { add_header Cache-Control "no-store" always; }
location = /sw.js       { add_header Cache-Control "no-cache" always; }
location /assets/ {
    try_files $uri =404;
    expires 1y;
    add_header Cache-Control "public, immutable" always;
    access_log off;
}
```

Ловушка: `add_header` в location **переопределяет** заголовки родительского уровня (не наследуются, если в location есть свои `add_header`): повторяйте нужные (security headers) или используйте include-файл.

## Сжатие: gzip и brotli

```nginx
gzip on;
gzip_comp_level 5;
gzip_min_length 1024;
gzip_vary on;
gzip_proxied any;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml font/ttf;

# brotli (модуль ngx_brotli): ~15–20% меньше gzip
brotli on;
brotli_comp_level 5;
brotli_types text/plain text/css application/json application/javascript image/svg+xml;
```

- **предсжатие при сборке** (`vite-plugin-compression`: `.gz` и `.br`) + `gzip_static on; brotli_static on;`: сжатие без нагрузки на CPU при запросе, можно максимальный уровень (9–11);
- не сжимать уже сжатое (png, jpg, woff2, видео);
- `Vary: Accept-Encoding` обязателен для кэшей/CDN.

## Заголовки безопасности для SPA

```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
add_header Content-Security-Policy "default-src 'self'; img-src 'self' data: https://cdn.example.com; connect-src 'self' https://api.example.com; frame-ancestors 'none'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Runtime-конфигурация

Один образ для всех окружений: `config.json` создаётся при старте контейнера из переменных окружения, а SPA читает его при загрузке (`fetch('/config.json')`).

```sh
# docker-entrypoint.d/40-config.sh (в образе nginx)
cat > /usr/share/nginx/html/config.json <<EOT
{"apiUrl":"${API_URL}","keycloakUrl":"${KEYCLOAK_URL}","release":"${RELEASE}"}
EOT
```

Или `envsubst` по шаблону. Это не место для секретов (файл публичный).

## Оптимизации

- **HTTP/2/3**, `sendfile on`, `tcp_nopush on`, `open_file_cache`;
- **CDN** перед Nginx: кэш статики, TLS, DDoS-защита;
- `Link: </assets/app.js>; rel=preload` / `103 Early Hints`;
- `etag on` (по умолчанию), `Last-Modified`;
- SPA с SSR — отдельный процесс (Node), nginx проксирует.

## Service Worker, версии, обновление

После деплоя у пользователя может остаться старый `index.html`, ссылающийся на удалённые файлы → 404 на чанки. Решения: **хранить предыдущие версии ассетов** некоторое время (не удалять старые файлы сразу), `no-cache` на `index.html`, обработка ошибки загрузки чанка в приложении (перезагрузка страницы), версионные каталоги.

## Kubernetes / Ingress

В образе — nginx со статикой (non-root `nginx-unprivileged`, порт 8080); Ingress маршрутизирует `/` на сервис фронтенда и `/api` на бэкенд; либо статика в объектном хранилище + CDN.

## Диагностика

| Симптом | Причина |
|---|---|
| 404 при обновлении страницы | нет `try_files ... /index.html` |
| Белая страница, ошибка MIME в консоли | fallback вернул HTML вместо js (неверный путь/`base` в Vite) |
| Пользователи видят старую версию | кэш `index.html`/SW, CDN |
| Ошибка загрузки чанка после релиза | старые ассеты удалены |
| Нет сжатия | `gzip_types`, прокси без `Accept-Encoding`, уже сжатый ответ |
| CORS | разные origin: использовать прокси `/api` |

## Вопросы с ответами

> [!question]- Зачем try_files с fallback на index.html?
> SPA обрабатывает маршруты на клиенте; при прямом заходе по такому URL сервер должен вернуть `index.html`, иначе будет 404.

> [!question]- Какие заголовки кэширования ставить для SPA?
> Для `index.html` — `no-cache`, для хэшированных ассетов — `max-age=31536000, immutable`, для runtime-конфига — `no-store`.

> [!question]- Как собрать один образ фронтенда для разных окружений?
> Не вшивать адреса при сборке, а генерировать `config.json` из переменных окружения при запуске контейнера.
