---
type: topic
domain: backend
stage: 3
section: "3.1"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981a6a9f0dc668b236e7a
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/logging, topic/observability, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Логирование: ILogger, уровни, structured logging, Serilog

↑ [[BE 3.1 Хост, конфигурация и middleware pipeline|3.1 Хост, конфигурация и middleware pipeline]] · ← [[BE 3.1.4 Options pattern — IOptions, IOptionsSnapshot, IOptionsMonitor, валидация|Предыдущая]] · → [[BE 3.1.6 HttpClient и IHttpClientFactory, HeaderPropagation|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





















































> [!info] Зачем это на собесе
> Логи — основа диагностики в проде. Спрашивают про уровни, structured logging и почему нельзя интерполировать строки.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`ILogger<T>` — абстракция логирования; провайдеры (Console, Serilog, OpenTelemetry) подключаются отдельно.

| Уровень | Назначение |
|---|---|
| Trace / Debug | детали отладки, выключены в проде |
| Information | значимые события работы |
| Warning | нештатная, но обработанная ситуация |
| Error | ошибка операции |
| Critical | сбой приложения |

```csharp
// Structured logging: шаблон + параметры, а не интерполяция
logger.LogInformation("Order {OrderId} paid by {UserId} in {ElapsedMs} ms", order.Id, userId, ms);

// Исключение передаём отдельным параметром
logger.LogError(ex, "Failed to process order {OrderId}", order.Id);
```

Шаблон сохраняется как имя события, а параметры становятся полями — в Loki/Elasticsearch можно фильтровать по `OrderId`.

### Source generator

```csharp
public static partial class Log
{
    [LoggerMessage(EventId = 1001, Level = LogLevel.Information, Message = "Order {OrderId} paid")]
    public static partial void OrderPaid(this ILogger logger, Guid orderId);
}
```

Нет аллокаций на boxing и парсинг шаблона; удобно для горячих путей.

### Serilog

```csharp
builder.Host.UseSerilog((ctx, lc) => lc
    .ReadFrom.Configuration(ctx.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console(new CompactJsonFormatter()));
```

Scopes и `LogContext` добавляют correlation id и tenant во все записи запроса.

## Нюансы и подводные камни

- `$"..."` в сообщении убивает structured logging и создаёт строку даже при выключенном уровне.
- Не логируйте пароли, токены, персональные данные и тела запросов целиком.
- Для тяжёлых аргументов проверяйте `logger.IsEnabled(LogLevel.Debug)`.
- Логируйте исключение один раз на границе, а не в каждом слое (иначе дубли).
- Уровни по категориям задаются в `Logging:LogLevel`; `Microsoft.AspNetCore` обычно `Warning`.

## Практика

1. Настройте вывод в JSON и добавьте `CorrelationId` через scope.
2. Перепишите три горячих лога на `LoggerMessage`.
3. Отправьте логи в Seq/Loki и найдите запрос по `OrderId`.

## Вопросы с ответами

> [!question]- Что такое structured logging?
> Логирование с сохранением шаблона и параметров как отдельных полей, что позволяет искать и агрегировать по значениям.

> [!question]- Почему не стоит использовать интерполяцию строк в логах?
> Теряется структура, строка формируется всегда и создаёт аллокации; шаблон с параметрами быстрее и удобнее для поиска.

> [!question]- Как связать логи одного запроса?
> Correlation/trace id в scope или через `Activity`/OpenTelemetry, добавляемый в каждую запись.

## Связанные темы

- [[N:3ea331048679814dbaadc2a67ef314e5]]
- [[N:3ea331048679813982d5cc11f4554a52]]
