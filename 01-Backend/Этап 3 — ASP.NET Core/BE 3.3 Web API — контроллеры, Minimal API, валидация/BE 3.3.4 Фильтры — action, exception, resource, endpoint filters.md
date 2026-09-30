---
type: topic
domain: backend
stage: 3
section: "3.3"
order: 4
status: todo
level: middle
notion_id: 3ea331048679812d8326dfc4bc122908
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/filters, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Фильтры: action, exception, resource, endpoint filters

↑ [[BE 3.3 Web API — контроллеры, Minimal API, валидация|3.3 Web API: контроллеры, Minimal API, валидация]] · ← [[BE 3.3.3 Валидация — DataAnnotations и FluentValidation|Предыдущая]] · → [[BE 3.3.5 DTO, маппинг и контракты API|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Часто путают фильтры и middleware. Нужно назвать разницу и порядок выполнения.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Фильтры выполняются внутри MVC/endpoint и знают контекст action, модель и результат.

| Тип фильтра | Когда | Пример |
|---|---|---|
| Authorization | самым первым | проверка политики |
| Resource | до/после остального (до binding) | кэш ответа |
| Action | до/после вызова action | логирование, валидация |
| Exception | необработанное исключение action | преобразование в ответ |
| Result | до/после исполнения результата | заголовки |
| Endpoint filter (Minimal API) | вокруг обработчика | валидация, идемпотентность |

```csharp
public class LogActionFilter(ILogger<LogActionFilter> log) : IAsyncActionFilter
{
    public async Task OnActionExecutionAsync(ActionExecutingContext ctx, ActionExecutionDelegate next)
    {
        log.LogInformation("Start {Action}", ctx.ActionDescriptor.DisplayName);
        var executed = await next();
        log.LogInformation("End {Action}", ctx.ActionDescriptor.DisplayName);
    }
}

builder.Services.AddControllers(o => o.Filters.Add<LogActionFilter>());
```

```csharp
// Minimal API
orders.MapPost("/", handler).AddEndpointFilter(async (ctx, next) =>
{
    var req = ctx.GetArgument<CreateOrderRequest>(0);
    if (req.Quantity <= 0) return Results.BadRequest("quantity");
    return await next(ctx);
});
```

Порядок: Authorization → Resource → (binding) → Action → выполнение → Result; Exception ловит ошибки action.

## Нюансы и подводные камни

- Фильтры с зависимостями регистрируйте как `[ServiceFilter]` или `[TypeFilter]`.
- Exception-фильтр не ловит исключения из middleware; для глобальной обработки — `IExceptionHandler`.
- Фильтры действуют только на endpoint-ы MVC; для статических файлов и не-MVC используйте middleware.
- Слишком много фильтров усложняет понимание порядка (`Order`).

## Практика

1. Напишите фильтр идемпотентности по заголовку `Idempotency-Key`.
2. Сделайте endpoint filter валидации на FluentValidation.
3. Сравните порядок выполнения на трёх уровнях: middleware → filter → action.

## Вопросы с ответами

> [!question]- Чем фильтр отличается от middleware?
> Middleware работает на уровне HTTP для любого запроса; фильтр — внутри MVC/endpoint и видит action, модель и результат.

> [!question]- Какие типы фильтров есть?
> Authorization, Resource, Action, Exception, Result; в Minimal API — endpoint filters.

> [!question]- Где лучше централизовать обработку ошибок?
> В `IExceptionHandler`/middleware, а не в exception-фильтрах: они не покрывают всё.

## Связанные темы

- [[N:3ea33104867981f59cb0d625e950c6cb]]
- [[N:3ea331048679818c931fc74c6d958606]]
