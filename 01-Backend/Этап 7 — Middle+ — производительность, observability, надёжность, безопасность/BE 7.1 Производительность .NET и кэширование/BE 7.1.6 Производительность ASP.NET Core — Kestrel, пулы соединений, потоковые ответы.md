---
type: topic
domain: backend
stage: 7
section: "7.1"
order: 6
status: todo
level: senior
notion_id: 3ea33104867981a7824ce4d2a5cd6c82
tags: [domain/backend, stage/7, level/senior, topic/dotnet, topic/aspnet, topic/performance, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Производительность ASP.NET Core: Kestrel, пулы соединений, потоковые ответы

↑ [[BE 7.1 Производительность .NET и кэширование|7.1 Производительность .NET и кэширование]] · ← [[BE 7.1.5 Стратегии кэша и инвалидация, cache stampede|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Какие рычаги есть у ASP.NET Core-приложения при высокой нагрузке.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Основные рычаги:

| Область | Что делать |
|---|---|
| Асинхронность | никакого `.Result`; async I/O по всей цепочке (см. [[N:3ea33104867981489552e5d712d06076]]) |
| ThreadPool | не блокировать потоки; при starvation — диагностика, а не `SetMinThreads` вслепую |
| Kestrel | HTTP/2/3, лимиты (`MaxConcurrentConnections`, `MaxRequestBodySize`), keep-alive |
| Соединения | `IHttpClientFactory`, пул БД (`Maximum Pool Size`), Redis multiplexer |
| Сериализация | `System.Text.Json` + source generators, стриминг больших ответов |
| Ответы | сжатие (Brotli), ETag/кэш, `IAsyncEnumerable` |
| EF/данные | проекции, `AsNoTracking`, пагинация, индексы |
| GC | Server GC в контейнерах, лимиты памяти, `TieredPGO`, ReadyToRun/NativeAOT для старта |
| Логирование | `LoggerMessage`, уровни, асинхронные sinks |

```csharp
// Потоковая выдача больших списков
app.MapGet("/export", async (AppDbContext db, HttpResponse res, CancellationToken ct) =>
{
    res.ContentType = "application/x-ndjson";
    await foreach (var o in db.Orders.AsNoTracking().AsAsyncEnumerable().WithCancellation(ct))
        await res.WriteAsync(JsonSerializer.Serialize(o) + "\n", ct);
});

// Source generator для JSON
[JsonSerializable(typeof(OrderDto))] partial class AppJsonContext : JsonSerializerContext;
builder.Services.ConfigureHttpJsonOptions(o => o.SerializerOptions.TypeInfoResolverChain.Insert(0, AppJsonContext.Default));
```

Метод: измерить (нагрузочный тест, метрики) → найти узкое место (обычно БД, внешние вызовы, а не код фреймворка) → исправить.

## Нюансы и подводные камни

- Kestrel не узкое место в типичных приложениях: чаще БД и блокировки.
- Лимиты CPU в контейнере влияют на число потоков и GC: задавайте `DOTNET_` переменные осознанно.
- Слишком большие пулы соединений перегружают БД.
- Буферизация всего ответа перед отправкой увеличивает память и задержку.
- Профилирование нужно на реалистичных данных.

## Практика

1. Проведите нагрузочный тест эндпоинта и найдите узкое место.
2. Включите JSON source generator и сравните аллокации.
3. Настройте потоковую выдачу экспорта на 1 млн записей.

## Вопросы с ответами

> [!question]- Что чаще всего тормозит ASP.NET Core-сервис?
> Блокирующий код, обращения к БД и внешним сервисам (N+1, отсутствие индексов), сериализация больших объектов.

> [!question]- Зачем потоковые ответы?
> Чтобы не держать весь ответ в памяти и начать отдачу раньше.

## Связанные темы

- [[N:3ea33104867981ec936ae21e56f183b5]]
- [[N:3ea331048679819ba14dfd93a8b0d68c]]
