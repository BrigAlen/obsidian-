---
type: topic
domain: devops
stage: 4
order: 2
status: todo
level: middle
tags: [domain/devops, stage/4, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 8
---

# Nginx как reverse proxy и API gateway для микросервисов

↑ [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Типовая схема: единый вход, маршрутизация по путям к микросервисам. Спрашивают заголовки, таймауты, безопасность.

## Схема

```text
Клиент ─HTTPS─▶ Nginx (TLS termination, маршрутизация, лимиты, кэш)
                   ├─ /          → frontend (SPA, статика)
                   ├─ /api/      → api-gateway / backend
                   ├─ /auth/     → Keycloak
                   ├─ /ws/       → WebSocket-сервис
                   └─ /files/    → MinIO (presigned)
```

Преимущества: единая точка входа и домен (без CORS между SPA и API), TLS в одном месте, скрытие внутренней топологии, маршрутизация, лимиты, кэш, логирование, смена бэкендов без изменений клиентов.

## Конфигурация

```nginx
upstream api      { server api:8080;      keepalive 32; }
upstream keycloak { server keycloak:8080; keepalive 8; }
upstream web      { server web:8080; }

server {
    listen 443 ssl;
    http2 on;
    server_name app.example.com;

    ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;

    # общие заголовки
    proxy_http_version 1.1;
    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Request-Id      $request_id;
    proxy_set_header Connection        "";

    location /api/ {
        proxy_pass http://api/;                 # слеш: /api/users → /users (префикс заменяется)
        proxy_connect_timeout 5s;
        proxy_send_timeout    30s;
        proxy_read_timeout    60s;
        proxy_next_upstream error timeout http_502 http_503;   # повтор на другом сервере (идемпотентные!)
        proxy_next_upstream_tries 2;
    }

    location /auth/ {
        proxy_pass http://keycloak;
        proxy_buffer_size 16k; proxy_buffers 8 16k;           # большие заголовки/cookies Keycloak
    }

    location / {
        proxy_pass http://web;
    }
}
```

## proxy_pass и слеш

| `location /api/` и | Запрос `/api/users` уходит как |
|---|---|
| `proxy_pass http://api;` | `/api/users` (без изменений) |
| `proxy_pass http://api/;` | `/users` (префикс `/api/` заменён на `/`) |

## Заголовки прокси

- `Host` — передаём исходный, если бэкенду нужен (иначе будет имя upstream);
- `X-Forwarded-For` (цепочка IP клиентов), `X-Forwarded-Proto` (http/https: бэкенд формирует корректные ссылки и редиректы), `X-Forwarded-Host`, `X-Real-IP`;
- приложение должно **доверять** этим заголовкам только от известного прокси: ASP.NET Core `UseForwardedHeaders` с `KnownProxies`/`KnownNetworks`; иначе подмена IP;
- `Forwarded` (RFC 7239) — стандартная форма;
- `X-Request-Id`/`traceparent` — сквозная корреляция и трассировка.

## Таймауты и буферы

| Директива | Смысл |
|---|---|
| `proxy_connect_timeout` | установка соединения с upstream |
| `proxy_send_timeout` / `proxy_read_timeout` | пауза между записью/чтением (не общее время) |
| `proxy_buffering on/off` | буферизация ответа (выключать для стриминга/SSE) |
| `proxy_buffer_size`, `proxy_buffers` | буферы заголовков/тела |
| `client_max_body_size` | максимум тела запроса (413) |
| `client_body_timeout`, `send_timeout` | таймауты клиента |
| `proxy_request_buffering off` | стримить загрузку на бэкенд |

Для долгих операций — увеличить `proxy_read_timeout` только на конкретном location; лучше асинхронные задачи.

## API gateway на Nginx

Функции: маршрутизация, TLS, `limit_req`, аутентификация (`auth_request` к внешнему сервису, проверка JWT), CORS, кэш ответов, переписывание путей, агрегация логов, канареечные маршруты (`split_clients`, `map`).

```nginx
location /api/ {
    auth_request /_auth;                       # подзапрос: 2xx — пропустить, 401/403 — отказать
    auth_request_set $user $upstream_http_x_user_id;
    proxy_set_header X-User-Id $user;
    proxy_pass http://api/;
}
location = /_auth { internal; proxy_pass http://auth-service/validate; proxy_pass_request_body off; proxy_set_header Content-Length ""; proxy_set_header X-Original-URI $request_uri; }
```

Для сложных сценариев — специализированные шлюзы (YARP, Kong, Envoy, Traefik, APISIX), Ingress в Kubernetes.

## Динамическое разрешение DNS

Nginx резолвит имена upstream **при старте** и кэширует: если контейнер пересоздан и IP изменился — 502. Решения: `resolver 127.0.0.11 valid=10s;` + `set $backend http://api:8080; proxy_pass $backend;` (переменная заставляет резолвить при запросе), либо перезагрузка nginx, либо Ingress/Traefik с обнаружением.

## Безопасность и надёжность

- `proxy_hide_header`, `server_tokens off`, удаление внутренних заголовков;
- запрет внутренних путей (`/metrics`, `/actuator`) извне или по IP (`allow/deny`);
- `limit_req`, `limit_conn` (см. edge-безопасность);
- `proxy_ssl_verify` при HTTPS к бэкенду;
- `proxy_next_upstream` не повторять небезопасные (POST) запросы автоматически;
- ограничение методов, размеров, заголовков (`large_client_header_buffers`);
- корректные коды при недоступности: `error_page 502 503 504 /maintenance.html;`.

## Диагностика

```bash
tail -f /var/log/nginx/error.log         # upstream timed out / connect() failed / no live upstreams
curl -v https://app.example.com/api/health
# в логе: $upstream_addr, $upstream_status, $upstream_response_time
```

| Симптом | Причина |
|---|---|
| 502 Bad Gateway | бэкенд недоступен/упал, неверный адрес/порт, закрыл соединение, протокол (http/https/grpc), устаревший IP |
| 504 Gateway Timeout | бэкенд не ответил за `proxy_read_timeout` |
| 413 | тело больше `client_max_body_size` |
| Неверные ссылки/редиректы (http вместо https) | не передан `X-Forwarded-Proto`/приложение его не учитывает |
| CORS-ошибки | разные origin: лучше единый домен через прокси |
| Потеряно реальное IP | нет `X-Forwarded-For` или приложение не обрабатывает |

## Вопросы с ответами

> [!question]- Чем proxy_pass http://api отличается от proxy_pass http://api/?
> Со слешем (с URI) префикс location заменяется на этот URI: `/api/users` → `/users`; без слеша путь передаётся как есть.

> [!question]- Зачем X-Forwarded-Proto?
> Бэкенд за прокси видит соединение по HTTP; заголовок сообщает исходную схему, чтобы приложение формировало правильные https-ссылки, cookie `Secure` и редиректы.

> [!question]- Почему после пересоздания контейнера Nginx отдаёт 502?
> Он закэшировал IP upstream при старте. Используйте `resolver` с переменной в `proxy_pass`, reload либо динамическое обнаружение (Traefik/Ingress).
