---
type: topic
domain: backend
stage: 3
section: "3.5"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981b28ed6dcb331e6f3c6
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/background, topic/jobs, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Фоновые задачи: IHostedService, BackgroundService, Worker, Hangfire и Quartz

↑ [[BE 3.5 Инфраструктура приложения — ошибки, health checks, фоновые задачи|3.5 Инфраструктура приложения: ошибки, health checks, фоновые задачи]] · ← [[BE 3.5.2 Health checks — liveness и readiness|Предыдущая]] · → [[BE 3.5.4 CORS, rate limiting, сжатие ответов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



























































> [!info] Зачем это на собесе
> Что использовать для периодических и отложенных задач и как не потерять работу при перезапуске.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```csharp
public class CleanupWorker(IServiceScopeFactory scopes, ILogger<CleanupWorker> log) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        using var timer = new PeriodicTimer(TimeSpan.FromMinutes(5));
        while (await timer.WaitForNextTickAsync(ct))
        {
            try
            {
                using var scope = scopes.CreateScope();
                await scope.ServiceProvider.GetRequiredService<ICleanup>().RunAsync(ct);
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                log.LogError(ex, "Cleanup failed");   // цикл не должен умирать
            }
        }
    }
}
builder.Services.AddHostedService<CleanupWorker>();
```

| Инструмент | Когда |
|---|---|
| `BackgroundService` | простые периодические/длительные процессы, обработка очереди в памяти |
| Worker Service | отдельный процесс без веб-части (консюмеры, обработчики) |
| Hangfire | отложенные/повторяющиеся задачи, ретраи, дашборд, хранение в БД |
| Quartz.NET | сложные расписания (cron), кластеризация |
| Outbox + очередь | надёжная доставка событий и задач |

## Нюансы и подводные камни

- Исключение в `ExecuteAsync` (.NET 6+) останавливает приложение по умолчанию (`BackgroundServiceExceptionBehavior.StopHost`) — ловите внутри цикла.
- Scoped-зависимости получайте через scope (см. [[N:3ea331048679816788e0df486d1eca06]]).
- В нескольких репликах задача выполнится в каждой: нужны distributed lock или планировщик со standalone-хранилищем.
- Задачи в памяти теряются при перезапуске; критичное — в очередь/БД.
- Уважайте `CancellationToken` для graceful shutdown.

## Практика

1. Напишите периодический воркер на `PeriodicTimer` с корректной обработкой ошибок.
2. Подключите Hangfire с PostgreSQL и добавьте recurring job.
3. Реализуйте distributed lock на Redis или advisory lock в PostgreSQL.

## Вопросы с ответами

> [!question]- Чем IHostedService отличается от BackgroundService?
> `BackgroundService` — базовый класс с готовым `ExecuteAsync` и управлением жизненным циклом поверх `IHostedService`.

> [!question]- Как выполнять задачу раз в час в нескольких репликах?
> Один планировщик с общим хранилищем (Hangfire/Quartz cluster) или distributed lock.

> [!question]- Hangfire или BackgroundService?
> Hangfire — когда нужны персистентность, ретраи и дашборд; BackgroundService — для лёгких задач.

## Связанные темы

- [[N:3ea33104867981e0adc9fe8799f5ec40]]
- [[N:3ea3310486798119982ad4f3f641704d]]
