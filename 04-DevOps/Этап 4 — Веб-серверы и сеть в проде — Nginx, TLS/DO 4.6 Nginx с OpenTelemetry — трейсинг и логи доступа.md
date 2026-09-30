---
type: topic
domain: devops
stage: 4
order: 6
status: todo
level: middle
tags: [domain/devops, stage/4, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 8
---

# Nginx с OpenTelemetry: трейсинг и логи доступа

↑ [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Nginx — первая точка входа запроса: именно там начинается трассировка и полезны структурированные access-логи.

## Что даёт

- **сквозная трассировка**: nginx создаёт/продолжает трейс (W3C `traceparent`), передаёт бэкендам, в трассе видно время на прокси и upstream;
- **access-логи с `trace_id`**: переход от лога к трейсу;
- метрики запросов, ошибок, задержек на входе.

## W3C Trace Context

Заголовок `traceparent: 00-<trace-id 32 hex>-<span-id 16 hex>-<flags>`. Если клиент его прислал — продолжаем; иначе создаём новый. Приложения (ASP.NET Core с OTel) автоматически продолжают трейс из входящих заголовков.

## Модуль OpenTelemetry для Nginx

Официальный `ngx_otel_module` (динамический модуль):

```nginx
load_module modules/ngx_otel_module.so;

http {
    otel_exporter {
        endpoint otel-collector:4317;          # OTLP gRPC (Collector)
        interval 5s;
        batch_size 512;
        batch_count 4;
    }
    otel_service_name nginx-edge;
    otel_resource_attr deployment.environment production;
    otel_trace on;                              # включить трассировку
    otel_trace_context propagate;               # extract + inject traceparent (extract | inject | propagate | ignore)

    server {
        listen 443 ssl;
        location /api/ {
            otel_span_name "api $request_method";
            otel_span_attr http.route "/api";
            proxy_pass http://api;
        }
        location /health { otel_trace off; return 200; }     # не трассировать шум
    }
}
```

Сэмплирование: `otel_trace $otel_sample_var` (`split_clients` для доли, например 10%). Переменные: `$otel_trace_id`, `$otel_span_id`, `$otel_parent_id`, `$otel_parent_sampled`.

Альтернативы: **Ingress-NGINX** с включённым OpenTelemetry (`enable-opentelemetry: "true"` в ConfigMap), **nginx-opentelemetry** (в образах Nginx), инструментированные Envoy/Traefik (встроенные OTLP), **eBPF-подходы** (Beyla, Odigos).

## Логи доступа с trace_id

```nginx
log_format json_otel escape=json
  '{'
    '"time":"$time_iso8601",'
    '"remote_addr":"$remote_addr",'
    '"request_id":"$request_id",'
    '"trace_id":"$otel_trace_id",'
    '"span_id":"$otel_span_id",'
    '"method":"$request_method",'
    '"uri":"$request_uri",'
    '"status":$status,'
    '"bytes_sent":$body_bytes_sent,'
    '"request_time":$request_time,'
    '"upstream_addr":"$upstream_addr",'
    '"upstream_status":"$upstream_status",'
    '"upstream_response_time":"$upstream_response_time",'
    '"http_host":"$host",'
    '"user_agent":"$http_user_agent",'
    '"referer":"$http_referer"'
  '}';
access_log /var/log/nginx/access.json json_otel;
# или в stdout для контейнера: access_log /dev/stdout json_otel;
```

Без модуля `trace_id` можно вытащить из `$http_traceparent` (через `map` с regex) и передавать в upstream (`proxy_set_header traceparent $http_traceparent`). Поле `request_id` (`$request_id`) добавляйте как `X-Request-Id` для сопоставления.

**Безопасность логов**: не логировать `Authorization`, cookie, токены в query (`$request_uri` может содержать секреты); персональные данные — минимизировать, маскировать.

## Collector и пайплайн

```text
nginx (OTLP трейсы) ─▶ OpenTelemetry Collector ─▶ Tempo / Jaeger / ClickHouse / SaaS
nginx (json-логи) ──▶ filelog receiver / Promtail / Vector ─▶ Loki / ClickHouse / Elasticsearch
nginx metrics: stub_status / nginx-prometheus-exporter / OTel nginx receiver ─▶ Prometheus
```

```yaml
# otel-collector: приём логов nginx из файлов
receivers:
  filelog:
    include: [/var/log/nginx/access.json]
    operators:
      - type: json_parser
        timestamp: { parse_from: attributes.time, layout: '%Y-%m-%dT%H:%M:%S%z' }
      - type: trace_parser
        trace_id: { parse_from: attributes.trace_id }
        span_id:  { parse_from: attributes.span_id }
```

Связка лога и трейса: Grafana «Logs → Trace» (derived field по `trace_id`), «Trace → Logs».

## Метрики Nginx

```nginx
server { listen 127.0.0.1:8080; location /stub_status { stub_status; allow 127.0.0.1; deny all; } }
```

Показывает: active connections, accepts/handled/requests, reading/writing/waiting. **nginx-prometheus-exporter** преобразует в Prometheus-метрики; более детальные метрики по статусам/путям — из access-логов (`mtail`, Vector, `nginx-vts`/OTel) или Ingress-NGINX (`nginx_ingress_controller_*`).

Золотые сигналы на входе: RPS, доля 4xx/5xx, p95/p99 `request_time` и `upstream_response_time`, насыщение (активные соединения, `worker_connections`), ошибки upstream.

## Что даёт трейс от nginx

- время, потерянное на edge (очереди, TLS, медленные клиенты) против времени приложения;
- какой upstream/под обработал запрос, ретраи (`proxy_next_upstream`);
- корреляция с логами и ошибками бэкендов; сквозные SLO.

## Практика и подводные камни

- единый формат контекста (**W3C**, не B3/смешанные) на всех уровнях;
- **сэмплирование** на edge (head-based) или в Collector (tail-based: хранить ошибки и медленные трейсы полностью);
- атрибуты: `service.name`, `deployment.environment`, `http.route`, `http.status_code`; не использовать высококардинальные значения в метриках (полный URL, user id);
- производительность: экспорт пакетами асинхронно, ограничение очередей; модуль трассировки добавляет небольшие накладные расходы;
- CDN/балансировщик перед nginx должны сохранять/передавать `traceparent`;
- для браузера: RUM-инструментация (OTel JS) добавляет `traceparent` в запросы: единый трейс от клиента до БД (CORS разрешить заголовок `traceparent`).

## Вопросы с ответами

> [!question]- Как связать лог nginx с трассой в Grafana?
> Писать в access-лог `trace_id` (из `$otel_trace_id` или заголовка `traceparent`) и настроить derived field/ссылку на трейс в источнике данных логов.

> [!question]- Зачем Nginx пробрасывает traceparent?
> Чтобы запрос имел единый trace от edge до БД: бэкенды продолжают трассу из заголовка, и время на прокси видно в общей диаграмме.

> [!question]- Какие метрики смотреть на nginx?
> RPS, доли 4xx/5xx, `request_time` и `upstream_response_time` (p95/p99), активные соединения, ошибки upstream (`upstream timed out`, 502/504).
