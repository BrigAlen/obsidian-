---
type: topic
domain: backend
stage: 1
section: "1.1"
order: 2
status: todo
level: junior
notion_id: 3ea331048679812882d9f5e746fcd550
tags: [domain/backend, stage/1, topic/networks, topic/http, level/junior, priority/should]
reviewed:
next_review:
priority: should
time: 6
---

# HTTP для бэкенда: методы, статусы, заголовки, keep-alive, HTTP/2 и HTTP/3

↑ [[BE 1.1 Сети и протоколы для бэкенда|1.1 Сети и протоколы для бэкенда]] · ← [[BE 1.1.1 Модель OSI и TCP-IP, TCP и UDP|Предыдущая]] · → [[BE 1.1.3 TLS, сертификаты, mTLS|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->
















> [!info] Зачем это на собесе
> API на ASP.NET Core — это HTTP. Интервьюер ждёт точного понимания семантики методов, статус-кодов, заголовков кэширования и разницы версий протокола. Базовая часть есть во фронтенд-теме, здесь — взгляд со стороны сервера.

## Подтемы
- [ ] Методы: безопасные, идемпотентные, кэшируемые
- [ ] Статус-коды, которые нужно выбирать уверенно
- [ ] Заголовки: content negotiation, кэш, трассировка, прокси
- [ ] Keep-alive и соединения
- [ ] HTTP/2 и HTTP/3

## Объяснение

### Методы и их свойства
- **Безопасные** (не меняют состояние): GET, HEAD, OPTIONS.
- **Идемпотентные** (повтор даёт тот же итог): GET, HEAD, OPTIONS, PUT, DELETE.
- **Не идемпотентные:** POST, PATCH (в общем случае).
- **Кэшируемые:** GET и HEAD (иногда POST с явными заголовками).

Серверные следствия:
- GET не должен менять данные: прокси, браузеры и краулеры повторяют и префетчат GET.
- PUT — полная замена ресурса по известному id (upsert). PATCH — частичное изменение (JSON Merge Patch или JSON Patch).
- POST для создания возвращает `201 Created` + заголовок `Location` + тело созданного ресурса.
- DELETE повторно → `204` или `404`: оба варианта допустимы, главное — стабильность.

### Статусы, которые должен уверенно выбирать бэкендер
- `200 OK`, `201 Created`, `202 Accepted` (принято к асинхронной обработке, например генерация отчёта), `204 No Content`.
- `304 Not Modified` — при условных запросах.
- `400 Bad Request` — синтаксически кривой запрос. `422 Unprocessable Entity` — валидный JSON, но бизнес-валидация не прошла (часто используют 400 с ProblemDetails — договоритесь в команде).
- `401` — нет или невалиден токен (+ заголовок `WWW-Authenticate`). `403` — нет прав.
- `404` — ресурса нет (иногда и для скрытия существования ресурса без прав).
- `409 Conflict` — конфликт состояния (дубликат, optimistic concurrency). `412 Precondition Failed` — не совпал `If-Match`.
- `429 Too Many Requests` + `Retry-After`.
- `500` — непредвиденная ошибка. `502/504` — проблема апстрима или прокси. `503` + `Retry-After` — сервис временно недоступен (перегрузка, деплой).

### Заголовки
- `Content-Type`/`Accept` — согласование формата (content negotiation).
- `Authorization: Bearer <jwt>`.
- Кэш: `Cache-Control` (`no-store`, `private`, `max-age`), `ETag` + `If-None-Match`, `If-Match` для оптимистичной конкурентности на запись.
- Трассировка: `traceparent` (W3C), `X-Request-Id`/`X-Correlation-Id`.
- За прокси: `X-Forwarded-For`, `X-Forwarded-Proto` (в ASP.NET Core нужен `UseForwardedHeaders`, иначе неверные схема и IP клиента).

### Keep-alive и соединения
HTTP/1.1 держит TCP-соединение открытым для следующих запросов, но в каждый момент по нему идёт один запрос (head-of-line blocking на уровне HTTP). Kestrel ограничивает число соединений и таймауты простоя.

### HTTP/2 и HTTP/3
- **HTTP/2:** бинарные фреймы, мультиплексирование потоков в одном TCP, сжатие заголовков HPACK, server push (устарел). **Обязателен для gRPC.**
- **HTTP/3:** QUIC поверх UDP, нет head-of-line blocking на транспорте, 0-RTT, миграция соединений. Kestrel поддерживает HTTP/3 (нужен TLS).

## Примеры в ASP.NET Core
```csharp
app.MapPost("/api/patients", async (CreatePatientDto dto, IPatientService svc, CancellationToken ct) =>
{
    var created = await svc.CreateAsync(dto, ct);
    return Results.Created($"/api/patients/{created.Id}", created);   // 201 + Location
});

app.MapGet("/api/patients/{id:guid}", async (Guid id, IPatientService svc, HttpContext ctx, CancellationToken ct) =>
{
    var patient = await svc.FindAsync(id, ct);
    if (patient is null) return Results.NotFound();
    var etag = $"\"{patient.Version}\"";
    if (ctx.Request.Headers.IfNoneMatch == etag) return Results.StatusCode(StatusCodes.Status304NotModified);
    ctx.Response.Headers.ETag = etag;
    return Results.Ok(patient);
});

app.MapPost("/api/reports", (ReportRequest r, IReportQueue q) =>
{
    var jobId = q.Enqueue(r);
    return Results.Accepted($"/api/reports/{jobId}/status", new { jobId });  // 202 для долгих операций
});
```
```csharp
// Kestrel: включить HTTP/1.1, HTTP/2 и HTTP/3
builder.WebHost.ConfigureKestrel(k =>
    k.ListenAnyIP(5001, o => { o.Protocols = HttpProtocols.Http1AndHttp2AndHttp3; o.UseHttps(); }));
```

## Нюансы и подводные камни
- gRPC без TLS требует явного HTTP/2 (h2c) на порту. Смешивать на одном порту без TLS HTTP/1.1 и HTTP/2 нельзя (нет ALPN).
- 500 с текстом исключения наружу — утечка внутренностей. Отдавайте ProblemDetails без стектрейса в проде.
- Не возвращайте 200 с `{ success: false }`: ломает мониторинг, ретраи и клиентов.
- `Retry-After` помогает клиентам и балансировщикам корректно повторять.

## Тестирование
Интеграционными тестами через `WebApplicationFactory` проверяйте статус, заголовки (`Location`, `ETag`) и тело, а не только сервисный слой.
```csharp
var response = await client.PostAsJsonAsync("/api/patients", dto);
response.StatusCode.Should().Be(HttpStatusCode.Created);
response.Headers.Location.Should().NotBeNull();
```

## Вопросы с ответами
> [!question]- Какие методы идемпотентны и почему это важно для бэкенда?
> GET, HEAD, OPTIONS, PUT, DELETE. Клиенты, прокси и библиотеки ретраев могут повторять их безопасно. Для POST нужна дедупликация через Idempotency-Key.

> [!question]- Какой статус вернуть при создании ресурса? При долгой асинхронной операции?
> 201 Created с Location и телом. Для долгой операции — 202 Accepted со ссылкой на статус задачи.

> [!question]- Когда 400, 409, 422?
> 400 — некорректный запрос (формат, типы). 422 — формат верный, но не прошла бизнес-валидация. 409 — конфликт с текущим состоянием (дубликат, версия устарела).

> [!question]- Зачем gRPC нужен HTTP/2?
> Мультиплексирование потоков, бинарные фреймы, trailers для статусов и двунаправленный стриминг есть только в HTTP/2 и выше.

> [!question]- Что сломается без UseForwardedHeaders за nginx?
> Приложение увидит IP прокси вместо клиента и схему http вместо https: неверные редиректы, ссылки, логи и ограничения по IP.

## Связанные темы
- Предыдущая: [[N:3ea33104867981b0ad32dbddff14402f]] · Следующая: [[N:3ea33104867981e388abd527913e239a]]
- HTTP со стороны фронта: [[N:3ea331048679817ab843d2d18cee2479]]
- Ответы и ProblemDetails: [[N:3ea3310486798146aa7cd46cc1613ab6]]
- REST-дизайн: [[N:3ea33104867981beb645e6208a37200e]]
- HTTP-кэширование: [[N:3ea331048679818ea678cc3a866d67e2]]
- Идемпотентность: [[N:3ea331048679816dbce2c367c9bda11e]]
