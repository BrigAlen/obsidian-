---
type: topic
domain: backend
stage: 3
section: "3.1"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981d5a91edcf41b2ae95a
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/middleware, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Middleware: конвейер, порядок, свои middleware

↑ [[BE 3.1 Хост, конфигурация и middleware pipeline|3.1 Хост, конфигурация и middleware pipeline]] · ← [[BE 3.1.1 Как устроен ASP.NET Core — Kestrel, хост, Program.cs, WebApplication|Предыдущая]] · → [[BE 3.1.3 Конфигурация — appsettings, окружения, переменные, секреты|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















































> [!info] Зачем это на собесе
> Порядок middleware — частая ловушка: «почему авторизация не срабатывает» и «где ставить CORS/обработчик ошибок».

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Middleware — компонент, который получает `HttpContext` и решает: обработать запрос сам или вызвать следующий (`next`). Конвейер строится как цепочка делегатов; ответ идёт обратно в обратном порядке.

```csharp
app.Use(async (ctx, next) =>
{
    var sw = Stopwatch.StartNew();
    await next(ctx);                       // вызов следующего
    ctx.Response.Headers["X-Elapsed-ms"] = sw.ElapsedMilliseconds.ToString();
});

app.Map("/health", b => b.Run(c => c.Response.WriteAsync("ok")));   // ветка
app.Run(ctx => ctx.Response.WriteAsync("terminal"));                // терминальный
```

### Рекомендуемый порядок

| Позиция | Middleware |
|---|---|
| 1 | `UseExceptionHandler` / `UseHsts` |
| 2 | `UseHttpsRedirection`, `UseForwardedHeaders` (за proxy раньше всех) |
| 3 | `UseStaticFiles` |
| 4 | `UseRouting` (неявно в minimal hosting) |
| 5 | `UseCors` |
| 6 | `UseAuthentication` |
| 7 | `UseAuthorization` |
| 8 | `UseRateLimiter`, `UseResponseCompression` |
| 9 | `MapControllers` / `MapGet` (endpoints) |

Правило: аутентификация → авторизация → endpoint; CORS до авторизации, чтобы preflight-запросы не отклонялись.

### Свой middleware

```csharp
public class CorrelationIdMiddleware(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext ctx)
    {
        var id = ctx.Request.Headers["X-Correlation-Id"].FirstOrDefault() ?? Guid.NewGuid().ToString();
        ctx.Response.Headers["X-Correlation-Id"] = id;
        using (logger.BeginScope(...)) { }   // по желанию
        await next(ctx);
    }
}

app.UseMiddleware<CorrelationIdMiddleware>();
```

Scoped-зависимости нужно получать в параметрах `InvokeAsync`, а не в конструкторе: middleware создаётся один раз (как singleton).

## Нюансы и подводные камни

- Нельзя писать в `Response` после того, как заголовки отправлены (`Response.HasStarted`).
- Не забывайте `await next(ctx)`; иначе цепочка обрывается, и часть логики не выполнится.
- Исключение в middleware выше обработчика ошибок попадёт клиенту как 500 без обработки.
- `IMiddleware` (фабричный) резолвится из DI на каждый запрос и позволяет scoped-зависимости в конструкторе.
- Тяжёлая работа в middleware выполняется для каждого запроса; кэшируйте и избегайте блокировок.

## Практика

1. Напишите middleware для correlation id и логируйте его во всех записях.
2. Поменяйте местами `UseAuthentication` и `UseAuthorization`, посмотрите поведение.
3. Сделайте middleware, замеряющий время и пишущий метрику.

## Вопросы с ответами

> [!question]- Почему важен порядок middleware?
> Каждый компонент видит запрос в порядке регистрации, а ответ в обратном. Например, авторизация без аутентификации не знает пользователя, а обработчик ошибок должен идти первым, чтобы перехватывать исключения остальных.

> [!question]- Чем Use, Run и Map отличаются?
> `Use` вызывает следующий, `Run` — терминальный, `Map` создаёт ветку конвейера по префиксу пути.

> [!question]- Как получить scoped-сервис в middleware?
> Через параметр `InvokeAsync`, либо реализовав `IMiddleware`.

> [!question]- Middleware или фильтр MVC?
> Middleware работает для всех запросов и не знает о контроллерах; фильтры — только для MVC/endpoints с доступом к контексту action и модели.

## Связанные темы

- [[N:3ea331048679810f8b4def6f1c5f7146]]
- [[N:3ea33104867981bf8a02c3a4b52c7ec7]]
