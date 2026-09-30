---
type: topic
domain: devops
stage: 4
order: 9
status: todo
level: middle
tags: [domain/devops, stage/4, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 7
---

# HTTP-1.1, HTTP-2 и HTTP-3: keep-alive, таймауты, буферы

↑ [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Различия версий HTTP и тонкая настройка keep-alive, таймаутов и буферов — частая тема для backend и DevOps.

## Эволюция

| Версия | Транспорт | Ключевые особенности | Проблемы |
|---|---|---|---|
| **HTTP/1.0** | TCP, соединение на запрос | простота | накладные расходы на соединения |
| **HTTP/1.1** (1997) | TCP | **keep-alive** по умолчанию, pipelining (на практике не используется), `Host`, chunked-кодирование, кэширование, range | **Head-of-Line blocking** на уровне запросов; браузеры открывают 6 соединений на хост |
| **HTTP/2** (2015) | TCP + TLS (на практике) | **мультиплексирование** многих потоков в одном соединении, **HPACK** сжатие заголовков, бинарный протокол, приоритеты, server push (устарел) | HOL на уровне TCP: потеря пакета замораживает все потоки |
| **HTTP/3** (2022) | **QUIC поверх UDP** | независимые потоки (нет TCP HOL), быстрый handshake (0/1-RTT), встроенный TLS 1.3, миграция соединения (смена сети без разрыва) | UDP блокируется в некоторых сетях; больше CPU; нужен fallback |

Повышение производительности HTTP/2 и HTTP/3 особенно заметно при множестве мелких ресурсов и на ненадёжных (мобильных) сетях. Прежние «оптимизации» HTTP/1.1 (спрайты, конкатенация, доменный шардинг) при HTTP/2 вредны или бесполезны.

## Keep-alive

Повторное использование TCP-соединения для нескольких запросов: экономия handshake (TCP + TLS).

```nginx
# клиент ↔ nginx
keepalive_timeout 65s;              # сколько держать простаивающее соединение
keepalive_requests 1000;            # максимум запросов на соединение (дальше — закрыть)

# nginx ↔ upstream (важно для производительности!)
upstream api {
    server 10.0.1.10:8080;
    keepalive 64;                   # пул простаивающих соединений к бэкенду на worker
    keepalive_timeout 60s;
    keepalive_requests 1000;
}
location /api/ {
    proxy_pass http://api;
    proxy_http_version 1.1;         # по умолчанию 1.0 — без keep-alive!
    proxy_set_header Connection "";
}
```

Согласование таймаутов: **keepalive-таймаут клиента/LB должен быть меньше таймаута бэкенда** (или наоборот согласованно), иначе возникают гонки: прокси отправил запрос в соединение, которое сервер уже закрыл → `502`/`connection reset`. Типично: таймаут idle у ALB 60 с → таймаут keep-alive на nginx/приложении > 60 с (например 75 с); у Kestrel `KeepAliveTimeout` (130 с по умолчанию).

## Включение HTTP/2 и HTTP/3 в Nginx

```nginx
server {
    listen 443 ssl;
    listen 443 quic reuseport;              # HTTP/3 (nginx ≥ 1.25)
    http2 on;
    http3 on;
    add_header Alt-Svc 'h3=":443"; ma=86400' always;   # сообщить клиентам о h3
    ssl_protocols TLSv1.2 TLSv1.3;
}
```

- HTTP/2 в браузерах требует TLS (ALPN `h2`); HTTP/3 — открыть **UDP/443** в firewall/security group;
- `curl --http2 -I https://...`, `curl --http3 -I ...`, `curl -w '%{http_version}'`; DevTools → колонка Protocol (`h2`, `h3`);
- CDN/балансировщики часто терминируют h2/h3 и говорят с origin по HTTP/1.1 — это нормально;
- gRPC требует HTTP/2 (`grpc_pass`, `listen ... http2`).

## Таймауты (клиентские и к upstream)

| Директива | Значение по умолчанию | Смысл |
|---|---|---|
| `client_header_timeout` | 60s | получение заголовков запроса |
| `client_body_timeout` | 60s | пауза между чтениями тела |
| `send_timeout` | 60s | пауза между отправкой клиенту |
| `keepalive_timeout` | 75s | idle keep-alive |
| `proxy_connect_timeout` | 60s | установка соединения с upstream (ставьте 3–5s) |
| `proxy_send_timeout` | 60s | пауза записи в upstream |
| `proxy_read_timeout` | 60s | пауза чтения от upstream |
| `lingering_timeout` | 5s | |

Замечание: таймауты `send/read` — **паузы между операциями**, а не общее время запроса. Общий лимит можно задать в приложении. Слишком большие значения — уязвимость к slowloris и расход ресурсов; слишком маленькие — обрывы долгих операций (тогда лучше делать операции асинхронными).

Цепочка таймаутов: **клиент → CDN/LB → nginx → приложение → БД**: внешний должен быть ≥ внутреннего, иначе клиент увидит ошибку/повтор раньше, чем завершится операция; согласуйте и настройте повторы идемпотентных запросов.

## Буферы

```nginx
client_body_buffer_size 16k;          # тело запроса в памяти (иначе во временный файл)
client_header_buffer_size 1k;
large_client_header_buffers 4 16k;    # большие заголовки/cookie (ошибка 400/431 при превышении)
client_max_body_size 20m;

proxy_buffering on;
proxy_buffer_size 8k;                 # буфер для заголовка ответа (большие cookie/токены → увеличить, 502 "upstream sent too big header")
proxy_buffers 8 16k;                  # буферы тела
proxy_busy_buffers_size 32k;
proxy_max_temp_file_size 0;           # не писать ответ во временный файл на диск
```

- `proxy_buffering off` — для SSE/стриминга/long-poll (`X-Accel-Buffering: no` от приложения);
- `proxy_request_buffering off` — стримить загрузки большие файлы сразу на бэкенд;
- ошибка **`upstream sent too big header`** при больших cookie/JWT (Keycloak!) → `proxy_buffer_size`, `proxy_buffers`;
- ошибка **`a client request body is buffered to a temporary file`** в логе — тело не поместилось в `client_body_buffer_size`.

## Chunked и сжатие, Range

- `Transfer-Encoding: chunked` — потоковая передача без `Content-Length`;
- `Content-Encoding: gzip/br/zstd`; `Range` — докачка и потоковое видео (`206 Partial Content`);
- `Expect: 100-continue`, `Connection: Upgrade` (WebSocket).

## Диагностика

```bash
curl -v --http1.1 https://example.com          # версия, заголовки, keep-alive
curl -w "connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer} total=%{time_total} ver=%{http_version}\n" -o /dev/null -s https://example.com
curl --http2 -I ...; curl --http3 -I ...
nghttp -nv https://example.com                 # детали HTTP/2
ss -ti state established '( dport = :8080 )'   # TCP-метрики, keepalive
```

В логах: `upstream prematurely closed connection`, `recv() failed (104: Connection reset by peer)` — гонка keep-alive, перезапуск upstream; `upstream timed out` — таймауты.

## Вопросы с ответами

> [!question]- Чем HTTP/2 отличается от HTTP/1.1?
> Бинарный протокол с мультиплексированием множества запросов в одном TCP-соединении, сжатием заголовков (HPACK) и приоритетами; устраняет head-of-line blocking на уровне запросов.

> [!question]- В чём преимущество HTTP/3?
> QUIC поверх UDP: независимые потоки без блокировки при потерях пакетов, быстрый handshake, миграция соединений между сетями.

> [!question]- Почему важно proxy_http_version 1.1 и пул keepalive к upstream?
> По умолчанию nginx общается с бэкендом по HTTP/1.0 без keep-alive: на каждый запрос новое соединение. Пул keep-alive сокращает задержки и нагрузку на бэкенд.
