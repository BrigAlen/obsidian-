---
type: topic
domain: backend
stage: 3
section: "3.5"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981469ec0c25216311408
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/errors, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Глобальная обработка ошибок: IExceptionHandler, middleware

↑ [[BE 3.5 Инфраструктура приложения — ошибки, health checks, фоновые задачи|3.5 Инфраструктура приложения: ошибки, health checks, фоновые задачи]] · → [[BE 3.5.2 Health checks — liveness и readiness|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






















> [!info] Зачем это на собесе
> «Как в вашем API обрабатываются исключения?» — ждут единое место, ProblemDetails и отсутствие утечки деталей.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Исключения не должны обрабатываться в каждом action `try/catch`. Один обработчик на входе конвейера преобразует их в ответ.

```csharp
public class GlobalExceptionHandler(ILogger<GlobalExceptionHandler> log) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(HttpContext ctx, Exception ex, CancellationToken ct)
    {
        var (status, title) = ex switch
        {
            NotFoundException   => (404, "Not found"),
            ConflictException   => (409, "Conflict"),
            ValidationException => (422, "Validation failed"),
            _                   => (500, "Unexpected error"),
        };
        if (status == 500) log.LogError(ex, "Unhandled exception {TraceId}", ctx.TraceIdentifier);

        ctx.Response.StatusCode = status;
        await ctx.Response.WriteAsJsonAsync(new ProblemDetails { Status = status, Title = title, Extensions = { ["traceId"] = ctx.TraceIdentifier } }, ct);
        return true;   // обработано
    }
}

builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
builder.Services.AddProblemDetails();
app.UseExceptionHandler();
```

| Способ | Комментарий |
|---|---|
| `IExceptionHandler` (.NET 8+) | рекомендуется, цепочка обработчиков |
| `UseExceptionHandler` + lambda | простой вариант |
| Exception filter MVC | только MVC, не ловит middleware |
| Result pattern | ожидаемые ошибки без исключений |

## Нюансы и подводные камни

- Исключения для ожидаемых бизнес-ситуаций дороги и «шумят»: рассмотрите `Result<T>`.
- Не возвращайте `ex.Message` и стек клиенту в проде.
- `UseExceptionHandler` ставьте первым.
- Логируйте один раз: обработчик логирует, остальные слои не дублируют.
- `OperationCanceledException` из-за отмены клиента — не ошибка (499/без ответа).

## Практика

1. Добавьте `IExceptionHandler` и маппинг доменных исключений в коды.
2. Добавьте `traceId` в ответ и найдите его в логах.
3. Замените исключения на `Result<T>` в одном сценарии.

## Вопросы с ответами

> [!question]- Где обрабатывать исключения в ASP.NET Core?
> В `IExceptionHandler`/`UseExceptionHandler` в начале конвейера, единый формат ProblemDetails.

> [!question]- Что вернуть клиенту при 500?
> Общее сообщение и `traceId`; детали — только в логах.

> [!question]- Исключения или Result?
> Исключения — для неожиданного; ожидаемые сбои (валидация, не найдено) удобнее и дешевле как значения.

## Связанные темы

- [[N:3ea33104867981bfb755f29c6b1cd640]]
- [[N:3ea33104867981e0adc9fe8799f5ec40]]
