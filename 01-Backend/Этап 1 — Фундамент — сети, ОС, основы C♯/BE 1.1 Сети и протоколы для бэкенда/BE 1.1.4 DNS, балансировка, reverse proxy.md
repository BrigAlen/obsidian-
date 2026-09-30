---
type: topic
domain: backend
stage: 1
section: "1.1"
order: 4
status: todo
level: junior
notion_id: 3ea331048679817aa584c01ff29564d5
tags: [domain/backend, stage/1, topic/networks, topic/infra, level/junior, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# DNS, балансировка, reverse proxy

↑ [[BE 1.1 Сети и протоколы для бэкенда|1.1 Сети и протоколы для бэкенда]] · ← [[BE 1.1.3 TLS, сертификаты, mTLS|Предыдущая]] · → [[BE 1.1.5 Стили API — REST, RPC, GraphQL, WebSocket, SSE|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->





























































> [!info] Зачем это на собесе
> В микросервисной архитектуре запрос проходит DNS, балансировщик и reverse proxy (в проекте — nginx-gateway перед GraphQL-шлюзом и public API). Нужно понимать, как запрос находит сервис и где могут теряться заголовки, IP и таймауты.

## Подтемы
- [ ] DNS для бэкенда: записи, TTL, внутренний DNS, кэш в .NET
- [ ] Балансировка L4 и L7, алгоритмы, health checks
- [ ] Reverse proxy: задачи и конфигурация nginx
- [ ] YARP и ForwardedHeaders в ASP.NET Core

## Объяснение

### DNS для бэкенда
- Записи: `A`/`AAAA` (IP), `CNAME` (псевдоним), `SRV` (хост и порт сервиса, используется в service discovery), `TXT`.
- **TTL** определяет, как долго клиенты кэшируют ответ. При переключении трафика TTL уменьшают заранее.
- **Внутренний DNS:** Docker Compose даёт встроенный DNS, и сервисы доступны по имени (`http://patient_storage:8080`). В Kubernetes — `service.namespace.svc.cluster.local`.
- .NET кэширует DNS внутри `SocketsHttpHandler` на время жизни соединения → `PooledConnectionLifetime`, чтобы подхватывать смену IP.
```csharp
services.AddHttpClient<PatientClient>()
    .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
    {
        PooledConnectionLifetime = TimeSpan.FromMinutes(2),  // пересоздавать соединения → свежий DNS
    });
```

### Балансировка нагрузки
- **L4 (транспортный):** распределяет TCP- и UDP-соединения, не видит HTTP. Быстро (IPVS, AWS NLB).
- **L7 (прикладной):** видит HTTP: маршрутизация по пути и заголовкам, TLS-терминация, sticky-сессии, ретраи (nginx, HAProxy, Envoy, YARP).

Алгоритмы: round robin, weighted, least connections, IP hash (консистентное хеширование для липкости).

Проверки здоровья: балансировщик исключает инстансы, не прошедшие health check, — отсюда важность `/health/ready`.

### Reverse proxy
Сервер-посредник перед приложениями. Задачи:
- единая точка входа, маршрутизация `/api/*` → сервисы, `/` → статика фронта;
- TLS-терминация, сжатие, кэш, ограничение размера тела, rate limiting;
- скрытие внутренней топологии.
```nginx
upstream gateway { server fusion_gateway:8080; keepalive 32; }
server {
  listen 443 ssl;
  location /graphql {
    proxy_pass http://gateway;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 60s;
  }
}
```

### YARP — reverse proxy на .NET
Библиотека Microsoft для построения прокси и API gateway прямо в ASP.NET Core (маршруты, кластеры, трансформации, балансировка).
```csharp
// ASP.NET Core за прокси: восстановить реальные IP и схему
builder.Services.Configure<ForwardedHeadersOptions>(o =>
{
    o.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    o.KnownNetworks.Clear(); o.KnownProxies.Clear();   // или явно указать IP прокси
});
app.UseForwardedHeaders();   // самым первым middleware
```

## Нюансы и подводные камни
- Sticky sessions — костыль для stateful-сервиса. Лучше stateless-сервисы и состояние в БД или Redis.
- Таймауты по цепочке должны уменьшаться к центру: клиент > nginx > gateway > сервис > БД. Иначе внешний уровень рвёт соединение, а работа внутри продолжается.
- Балансировщик L7 и долгие соединения (WebSocket, gRPC-стримы): нужны `Upgrade`-заголовки и увеличенные таймауты.
- HTTP/2 к бэкенду из nginx для gRPC — `grpc_pass`, а не `proxy_pass`.
- Кэш DNS в долгоживущих клиентах — причина «сервис переехал, а трафик идёт на старый IP».

## Вопросы с ответами
> [!question]- Чем балансировщик L4 отличается от L7?
> L4 работает с TCP и UDP-соединениями, не видит HTTP, очень быстрый. L7 понимает HTTP: маршрутизация по путям и заголовкам, TLS-терминация, ретраи, sticky, но дороже.

> [!question]- Зачем reverse proxy перед сервисами?
> Единая точка входа, маршрутизация, TLS, сжатие, кэш, лимиты, защита и скрытие внутренней топологии, балансировка между инстансами.

> [!question]- Как сервисы находят друг друга в Docker Compose и Kubernetes?
> Через встроенный DNS по имени сервиса: в Compose — имя сервиса в общей сети, в Kubernetes — Service с DNS-именем и балансировкой между подами.

> [!question]- Какие алгоритмы балансировки знаете?
> Round robin, weighted round robin, least connections, IP hash или консистентное хеширование, random with two choices.

## Связанные темы
- Предыдущая: [[N:3ea33104867981e388abd527913e239a]] · Следующая: [[N:3ea33104867981bb8a3cd70eff7d424c]]
- Nginx как reverse proxy: [[N:3ea331048679813ab4cef1ea50e395bd]]
- API Gateway и BFF: [[N:3ea33104867981cfa283cc1de55bd7d1]]
- Health checks: [[N:3ea33104867981e0adc9fe8799f5ec40]]
- Балансировка L4/L7 в DevOps: [[N:3ea33104867981a0a753f19cd10dd6a4]]
- Масштабирование: [[N:3ea331048679819193bff686992609a1]]
