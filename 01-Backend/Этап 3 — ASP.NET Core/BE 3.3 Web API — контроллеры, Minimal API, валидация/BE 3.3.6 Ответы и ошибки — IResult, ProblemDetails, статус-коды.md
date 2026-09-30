---
type: topic
domain: backend
stage: 3
section: "3.3"
order: 6
status: todo
level: middle
notion_id: 3ea3310486798146aa7cd46cc1613ab6
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/http, topic/errors, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Ответы и ошибки: IResult, ProblemDetails, статус-коды

↑ [[BE 3.3 Web API — контроллеры, Minimal API, валидация|3.3 Web API: контроллеры, Minimal API, валидация]] · ← [[BE 3.3.5 DTO, маппинг и контракты API|Предыдущая]] · → [[BE 3.3.7 OpenAPI и Swagger, версионирование API|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





































> [!info] Зачем это на собесе
> Знание статус-кодов и единого формата ошибок (RFC 9457) — признак зрелого API-дизайна.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Код | Когда |
|---|---|
| 200 OK | успешное чтение/операция с телом |
| 201 Created | создан ресурс + заголовок `Location` |
| 202 Accepted | принято, обработка асинхронна |
| 204 No Content | успех без тела (обновление, удаление) |
| 400 Bad Request | неверный формат запроса |
| 401 Unauthorized | не аутентифицирован |
| 403 Forbidden | нет прав |
| 404 Not Found | ресурс не найден |
| 409 Conflict | конфликт состояния/версии |
| 422 Unprocessable Entity | синтаксис верен, бизнес-правило нарушено |
| 429 Too Many Requests | лимит запросов |
| 500 / 503 | ошибка сервера / временная недоступность |

```csharp
app.MapPost("/orders", async (CreateOrderRequest r, IOrderService s) =>
{
    var id = await s.CreateAsync(r);
    return Results.Created($"/orders/{id}", new { id });
});

app.MapGet("/orders/{id:guid}", async (Guid id, IOrderService s) =>
    await s.FindAsync(id) is { } o ? Results.Ok(o) : Results.Problem(statusCode: 404, title: "Order not found"));

// TypedResults для OpenAPI-типизации
static async Task<Results<Ok<OrderDto>, NotFound>> Get(Guid id, IOrderService s) => ...
```

### ProblemDetails (RFC 9457)

Единый формат ошибки: `type`, `title`, `status`, `detail`, `instance` и расширения (`errors`, `traceId`).

```csharp
builder.Services.AddProblemDetails(o => o.CustomizeProblemDetails = c =>
    c.ProblemDetails.Extensions["traceId"] = c.HttpContext.TraceIdentifier);
```

## Нюансы и подводные камни

- 200 с текстом «ошибка» в теле — антипаттерн.
- Не отдавайте стек и внутренние детали в production.
- 401 vs 403: без токена/невалидный — 401; токен валиден, но прав нет — 403.
- 404 вместо 403 иногда используют, чтобы не раскрывать существование ресурса.
- Идемпотентность: PUT/DELETE идемпотентны, POST — нет (нужен `Idempotency-Key`).

## Практика

1. Включите ProblemDetails и убедитесь, что все ошибки приходят в едином формате.
2. Верните `TypedResults` и посмотрите схему в Swagger.
3. Реализуйте 409 при конфликте версии (ETag/rowversion).

## Вопросы с ответами

> [!question]- 401 или 403?
> 401 — не удалось аутентифицировать, 403 — пользователь известен, но действие запрещено.

> [!question]- Что такое ProblemDetails?
> Стандартный JSON-формат ошибки HTTP API с полями type/title/status/detail/instance.

> [!question]- 400 или 422?
> 400 — запрос не разобран или структурно неверен; 422 — формально корректен, но нарушает бизнес-правила. Главное — единая договорённость в API.

## Связанные темы

- [[N:3ea331048679818c931fc74c6d958606]]
- [[N:3ea331048679816ca2a9e01efe418d51]]
