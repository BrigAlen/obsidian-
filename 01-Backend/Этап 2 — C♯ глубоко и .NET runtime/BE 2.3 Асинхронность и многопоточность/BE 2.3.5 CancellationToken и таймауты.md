---
type: topic
domain: backend
stage: 2
section: "2.3"
order: 5
status: todo
level: middle
notion_id: 3ea3310486798196b8aefe56a6e542b8
tags: [domain/backend, stage/2, level/middle, topic/cancellation, topic/timeouts, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# CancellationToken и таймауты

↑ [[BE 2.3 Асинхронность и многопоточность|2.3 Асинхронность и многопоточность]] · ← [[BE 2.3.4 ValueTask и аллокации|Предыдущая]] · → [[BE 2.3.6 Синхронизация — lock, Monitor, SemaphoreSlim, Interlocked, ReaderWriterLockSlim|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Отмена и таймауты — признак зрелого бэкенд-кода. Спросят, как прервать долгий запрос, когда клиент закрыл соединение, как задать таймаут на операцию, чем `CancellationTokenSource` отличается от токена и что делать с `OperationCanceledException`.

## Объяснение

### Кооперативная отмена
Отмена в .NET **кооперативная**: одна сторона **просит** остановиться, другая **сама проверяет** и завершается.
- `CancellationTokenSource` (CTS) — источник: вызывает `Cancel()`.
- `CancellationToken` — токен: передаётся в методы и проверяется.
```csharp
using var cts = new CancellationTokenSource();
var task = ProcessAsync(cts.Token);
cts.Cancel();                                   // просьба остановиться
try { await task; } catch (OperationCanceledException) { /* штатная отмена */ }

async Task ProcessAsync(CancellationToken ct)
{
    foreach (var item in items)
    {
        ct.ThrowIfCancellationRequested();       // проверка между шагами
        await HandleAsync(item, ct);             // передаём токен вниз
    }
}
```

### Что делать в коде
- **Принимать** `CancellationToken ct` последним параметром (по умолчанию `= default`) во всех асинхронных методах.
- **Передавать** его в каждый вложенный вызов: `HttpClient`, EF Core (`ToListAsync(ct)`), `Task.Delay`, `Stream.ReadAsync`.
- Проверять в собственных циклах: `ct.ThrowIfCancellationRequested()` или `ct.IsCancellationRequested`.
- `OperationCanceledException` (и `TaskCanceledException`) — **штатная** реакция на отмену, не ошибка: не логируйте как error.

### В ASP.NET Core
```csharp
app.MapGet("/api/report/{id}", async (Guid id, IReportService svc, CancellationToken ct) =>
    Results.File(await svc.BuildAsync(id, ct), "application/pdf"));
```
Токен запроса (`HttpContext.RequestAborted`) срабатывает, если клиент закрыл соединение. В контроллерах и Minimal API его можно просто добавить параметром.

### Таймауты
```csharp
// 1) на группу операций: связанный токен
using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(5));
using var linked = CancellationTokenSource.CreateLinkedTokenSource(ct, timeout.Token);   // отмена клиента ИЛИ таймаут
var data = await client.GetAsync(url, linked.Token);

// 2) CancelAfter
cts.CancelAfter(TimeSpan.FromSeconds(30));

// 3) .NET 6+: ограничить время ожидания задачи (сама операция не отменяется!)
var result = await slowTask.WaitAsync(TimeSpan.FromSeconds(5), ct);

// 4) HttpClient.Timeout (по умолчанию 100 с) и политики Polly / Microsoft.Extensions.Http.Resilience
builder.Services.AddHttpClient<Api>().AddStandardResilienceHandler();
```
Различать причину: `catch (OperationCanceledException) when (timeout.IsCancellationRequested)` — таймаут; `when (ct.IsCancellationRequested)` — отмена вызывающего.

### Регистрация обратных вызовов и освобождение ресурсов
```csharp
await using var registration = ct.Register(() => connection.Cancel());   // отменить нативный ресурс
```
`CancellationTokenSource` держит таймер и регистрации: **освобождайте** (`Dispose`), особенно при `CancelAfter`.

### Отмена в фоновых сервисах
`BackgroundService.ExecuteAsync(CancellationToken stoppingToken)` — токен срабатывает при остановке приложения (SIGTERM). Все циклы и задержки должны его учитывать, иначе будет принудительное завершение по истечении `ShutdownTimeout`.
```csharp
protected override async Task ExecuteAsync(CancellationToken stoppingToken)
{
    using var timer = new PeriodicTimer(TimeSpan.FromSeconds(10));
    while (await timer.WaitForNextTickAsync(stoppingToken))
        await DoWorkAsync(stoppingToken);
}
```

## Нюансы и подводные камни
- Отмена ничего не гарантирует: если код не проверяет токен, он продолжит работу. Метод без токена нельзя отменить.
- `WaitAsync(timeout)` **не отменяет** саму операцию: она продолжит выполняться в фоне. Для реальной остановки нужен токен в самой операции.
- Отмена **после** `commit` транзакции или отправки сообщения не откатывает результат: продумайте идемпотентность.
- `Task.Delay` без токена — «зависший» таймер и задержка остановки приложения.
- Ловить `OperationCanceledException` слишком широко (`catch (Exception)`) — глушить отмену; отделяйте.
- `CancellationToken.None` в цепочке «разрывает» отмену: клиент ушёл, а запрос к БД продолжается.
- Не передавайте токен запроса в фоновую работу, которая должна пережить запрос: он отменится вместе с запросом.

## Практика
- Добавить токен во все методы сервиса и проверить, что закрытие соединения клиентом обрывает запрос в БД.
- Реализовать метод с общим таймаутом на несколько вложенных вызовов через `CreateLinkedTokenSource`.
- Найти в проекте `Task.Delay` без токена и исправить.

## Вопросы с ответами
> [!question]- Как работает отмена в .NET?
> Кооперативно: `CancellationTokenSource` выставляет запрос на отмену, а код, получивший `CancellationToken`, сам проверяет его или передаёт в вызовы, поддерживающие отмену. Обычно завершение выражается `OperationCanceledException`.

> [!question]- Чем `CancellationToken` отличается от `CancellationTokenSource`?
> Токен только читается и передаётся в методы. Источник управляет отменой (`Cancel`, `CancelAfter`) и выдаёт токены.

> [!question]- Как реализовать таймаут на группу операций и при этом учитывать отмену клиента?
> Создать `CancellationTokenSource` с таймаутом и связать с исходным токеном через `CreateLinkedTokenSource`; передавать связанный токен вниз.

> [!question]- Должна ли отмена логироваться как ошибка?
> Нет. Это штатное поведение (клиент закрыл соединение, приложение останавливается). Ловите `OperationCanceledException` отдельно и не поднимайте уровень error.

> [!question]- Чем `WaitAsync(timeout)` отличается от токена с таймаутом?
> `WaitAsync` прекращает ожидание, но операция продолжает работать в фоне. Токен с таймаутом действительно просит операцию остановиться, если она его учитывает.

## Связанные темы
- Предыдущая: [[N:3ea33104867981379a84f8c9a6af61e0]] · Следующая: [[N:3ea33104867981fea69fce768dc3e0dd]]
- Task и TPL: [[N:3ea33104867981b6accfed9422b4bec4]]
- Фоновые задачи: [[N:3ea3310486798174a48de13989e34a6e]]
- Устойчивость: retry, timeout, circuit breaker: [[N:3ea331048679817f9ee3ca793b9036a9]]
- AbortController в JS: [[N:3ea3310486798125aed9f655f8593986]]
