---
type: topic
domain: backend
stage: 7
section: "7.2"
order: 2
status: todo
level: senior
notion_id: 3ea33104867981edac43cf84838e178a
tags: [domain/backend, stage/7, level/senior, topic/observability, topic/logging, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Структурные логи: Serilog, корреляция, уровни, что не логировать

↑ [[BE 7.2 Observability — логи, метрики, трейсинг, OpenTelemetry|7.2 Observability: логи, метрики, трейсинг, OpenTelemetry]] · ← [[BE 7.2.1 Три столпа observability — логи, метрики, трейсы|Предыдущая]] · → [[BE 7.2.3 OpenTelemetry в .NET — SDK, инструментация, Activity, Meter|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->
























> [!info] Зачем это на собесе
> Практика логирования: какие уровни, как коррелировать, что нельзя писать.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Основы логирования в ASP.NET Core — в [[N:3ea33104867981a6a9f0dc668b236e7a]]. Здесь — эксплуатационные правила.

| Уровень | Когда |
|---|---|
| Error | операция не удалась, требуется внимание |
| Warning | нештатно, но обработано (ретрай, деградация) |
| Information | ключевые бизнес-события (заказ создан) |
| Debug/Trace | детали, в проде выключены |

Правила:

- Структурные логи (JSON) с полями: `timestamp`, `level`, `message template`, `trace_id`, `span_id`, `service`, `env`, `user_id` (идентификатор, а не персональные данные).
- **Корреляция**: `Activity.Current?.TraceId` автоматически попадает в логи при включённом `IncludeScopes`/Serilog `Enrich.WithSpan()`.
- Логируйте на границах (вход/выход, обращения к внешним системам), а не в каждом методе.
- Исключение логируется один раз, там, где обрабатывается.
- Семплирование шумных логов и ограничение частоты.

```csharp
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft.AspNetCore", LogEventLevel.Warning)
    .Enrich.FromLogContext().Enrich.WithProperty("service", "orders")
    .Destructure.ByTransforming<User>(u => new { u.Id })     // не логировать лишние поля
    .WriteTo.Console(new RenderedCompactJsonFormatter())
    .CreateLogger();
```

**Что не логировать**: пароли, токены, ключи, номера карт, паспортные и медицинские данные, тела запросов целиком, заголовок `Authorization`. Применяйте маскирование и allowlist полей.

## Нюансы и подводные камни

- Логи в файлах в контейнере: пишите в stdout, собирает агент (Promtail, Fluent Bit, OTel Collector).
- Логирование синхронно замедляет запросы: асинхронные sinks, буферы.
- Логи на Debug в проде включайте временно и точечно.
- Стоимость хранения: retention и уровни по окружениям.

## Практика

1. Настройте JSON-логи с `trace_id` и найдите запрос по нему в Loki/Elastic.
2. Добавьте маскирование секретов.
3. Снизьте объём логов на 50% без потери диагностической ценности.

## Вопросы с ответами

> [!question]- Что нельзя логировать?
> Секреты, персональные и платёжные данные, токены и полные тела запросов.

> [!question]- Как связать логи разных сервисов?
> Общий `trace_id` (W3C traceparent) в каждой записи.

## Связанные темы

- [[N:3ea331048679819ba14dfd93a8b0d68c]]
- [[N:3ea331048679815b881ac9af6cde7167]]
