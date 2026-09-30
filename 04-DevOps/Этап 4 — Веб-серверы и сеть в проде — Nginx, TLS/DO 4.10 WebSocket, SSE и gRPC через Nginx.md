---
type: topic
domain: devops
stage: 4
order: 10
status: todo
level: middle
tags: [domain/devops, stage/4, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 8
---

# WebSocket, SSE и gRPC через Nginx

↑ [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Долгоживущие соединения требуют особых настроек прокси; типичные проблемы — обрывы через 60 секунд и буферизация SSE.

## WebSocket

Протокол двусторонней связи поверх одного TCP-соединения: начинается HTTP-запросом с `Upgrade: websocket` (код 101 Switching Protocols), затем обмен кадрами.

### Настройка Nginx

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    ''      close;
}

upstream ws_backend { server ws:8080; }

server {
    location /ws/ {
        proxy_pass http://ws_backend;
        proxy_http_version 1.1;                          # обязателен
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 3600s;                        # по умолчанию 60s — соединение рвётся при молчании
        proxy_send_timeout 3600s;
        proxy_buffering off;
    }
}
```

**Типичные проблемы**:

| Симптом | Причина |
|---|---|
| 400/426, нет апгрейда | нет `Upgrade`/`Connection`, `proxy_http_version 1.0` |
| Соединение рвётся через 60 с | `proxy_read_timeout` (а также таймауты LB/CDN: ALB 60 с, Cloudflare ~100 с) |
| Соединения разрываются по одному при reload | старые worker держат соединения; `worker_shutdown_timeout` |
| Клиентам «липнет» один бэкенд | нужна sticky-сессия или состояние в общем хранилище |
| Не работает за CDN/LB | не включена поддержка WebSocket или HTTP/1.1 |

Практики:

- **ping/pong** (heartbeat, каждые 20–30 с) поддерживает соединение и обнаруживает обрыв на уровне приложения и промежуточных устройств;
- **автоматическое переподключение** клиента с backoff и jitter, восстановление состояния (последний `seq`);
- аутентификация при подключении (токен в первом сообщении/субпротоколе/cookie; токен в query логируется — осторожно);
- ограничение числа соединений (`limit_conn`), размер сообщений, проверка `Origin` на сервере (CSWSH);
- масштабирование: соединения привязаны к инстансу → **backplane** (Redis pub/sub, Azure SignalR, NATS, Kafka) для рассылки между инстансами (SignalR с Redis);
- `worker_connections` — каждое WebSocket удерживает 2 соединения (клиент + upstream); `ulimit -n`; мониторинг числа соединений;
- graceful drain при деплое (уведомить клиентов о переподключении).

## SSE (Server-Sent Events)

Однонаправленный поток **от сервера к клиенту** поверх обычного HTTP (`Content-Type: text/event-stream`), авто-переподключение в браузере (`EventSource`), идентификаторы событий (`Last-Event-ID`). Проще WebSocket, работает через обычные прокси/HTTP/2.

```nginx
location /events/ {
    proxy_pass http://api;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;                 # иначе события копятся в буфере
    proxy_cache off;
    proxy_read_timeout 3600s;
    chunked_transfer_encoding on;        # по умолчанию
    add_header X-Accel-Buffering no;     # или приложение отправляет этот заголовок
}
```

Проблемы: буферизация и сжатие (gzip может задерживать события — исключить `text/event-stream` из `gzip_types`), таймауты простоя (шлите комментарии-`:keepalive` раз в 15–30 с), лимит 6 соединений на домен в HTTP/1.1 (в HTTP/2 — множество потоков), HTTP/1.1 без keep-alive к upstream.

| | WebSocket | SSE |
|---|---|---|
| Направление | двустороннее | сервер → клиент |
| Протокол | свой поверх TCP | HTTP |
| Автопереподключение | вручную | встроено |
| Бинарные данные | да | нет (текст) |
| Прокси/HTTP/2 | требует настройки upgrade | просто |
| Применение | чат, игры, совместное редактирование | уведомления, ленты, прогресс |

## gRPC через Nginx

gRPC — HTTP/2 с Protobuf; нужен модуль `ngx_http_grpc_module`.

```nginx
server {
    listen 443 ssl;
    http2 on;
    ssl_certificate ...; ssl_certificate_key ...;

    location /orders.OrderService/ {                       # путь = /{пакет}.{Сервис}/{Метод}
        grpc_pass grpc://orders:5000;                      # grpcs:// для TLS до бэкенда
        grpc_read_timeout 300s;
        grpc_send_timeout 300s;
        grpc_set_header X-Real-IP $remote_addr;
        client_max_body_size 0;
        error_page 502 = /error502grpc;
    }
    location = /error502grpc {
        internal;
        default_type application/grpc;
        add_header grpc-status 14;
        add_header grpc-message "unavailable";
        return 204;
    }
}
```

Особенности:

- **HTTP/2 end-to-end** (клиент ↔ nginx ↔ сервис); `grpc_pass` вместо `proxy_pass`;
- долгие стримы: таймауты `grpc_read_timeout`; **keepalive pings** на клиенте/сервере согласовать с прокси и LB;
- **балансировка gRPC на L4 неэффективна**: одно долгоживущее HTTP/2-соединение «прилипает» к одному поду → нужна L7-балансировка (Envoy, nginx `grpc_pass` с upstream, Linkerd) или клиентская балансировка (headless service + gRPC load balancing);
- браузеры не говорят gRPC напрямую: **gRPC-Web** (через Envoy/`grpc-web` прокси) или JSON-транскодинг (ASP.NET Core gRPC JSON transcoding);
- TLS и ALPN `h2`; при проблемах проверять `grpcurl`, `curl --http2-prior-knowledge`;
- ошибки: `upstream sent no valid HTTP/2`, `502` при протокольных несовпадениях (`proxy_pass` вместо `grpc_pass`), лимиты размера сообщений.

## Kubernetes Ingress

Ingress-NGINX аннотации: `nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"`, `backend-protocol: "GRPC"`, `proxy-buffering: "off"`, `websocket-services`, `affinity: cookie` (sticky). Gateway API (`GRPCRoute`, `HTTPRoute`) и Envoy/Istio поддерживают gRPC нативно.

## Диагностика

```bash
websocat wss://example.com/ws/            # клиент WebSocket
wscat -c wss://example.com/ws/
curl -N -H "Accept: text/event-stream" https://example.com/events/     # SSE (-N без буфера)
grpcurl -d '{"id":1}' example.com:443 orders.OrderService/Get
curl -i -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" https://example.com/ws/
```

## Вопросы с ответами

> [!question]- Что нужно настроить в nginx для WebSocket?
> HTTP/1.1 к upstream, заголовки `Upgrade` и `Connection` через `map`, увеличенные `proxy_read_timeout`/`proxy_send_timeout`, отключить буферизацию; учесть таймауты LB/CDN.

> [!question]- Почему SSE «не приходит» клиенту сразу?
> Nginx буферизует ответ (и/или gzip). Отключить `proxy_buffering`, исключить `text/event-stream` из сжатия, отправлять `X-Accel-Buffering: no` и периодические keepalive-комментарии.

> [!question]- Почему балансировка gRPC на L4 работает плохо?
> gRPC использует долгоживущие мультиплексированные HTTP/2-соединения; L4-балансировщик распределяет соединения, а не запросы, и нагрузка концентрируется на одном бэкенде. Нужна L7- или клиентская балансировка.
