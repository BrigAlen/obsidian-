---
type: topic
domain: backend
stage: 2
section: "2.3"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981b6accfed9422b4bec4
tags: [domain/backend, stage/2, level/middle, topic/tasks, topic/tpl, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Task и TPL

↑ [[BE 2.3 Асинхронность и многопоточность|2.3 Асинхронность и многопоточность]] · ← [[BE 2.3.1 Thread и ThreadPool|Предыдущая]] · → [[BE 2.3.3 async-await изнутри — state machine, SynchronizationContext, ConfigureAwait|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> `Task` — основа асинхронности в .NET. Вопросы: чем Task отличается от Thread, что такое Task.Run и когда он нужен, как работают WhenAll и WhenAny, как обрабатывать исключения нескольких задач.

## Объяснение

### Task — обещание результата, а не поток

`Task` / `Task<T>` — объект, представляющий **асинхронную операцию** и её будущий результат. Он **не равен потоку**:
- I/O-задача (запрос к БД, HTTP) во время ожидания **не занимает ни одного потока**: ОС уведомит о завершении.
- CPU-задача через `Task.Run` выполняется на потоке пула.
Состояния: `Created`, `WaitingForActivation`, `Running`, `RanToCompletion`, `Faulted`, `Canceled`.

### Task.Run

Выполнить **CPU-bound** работу на пуле потоков, чтобы не блокировать текущий поток.
```csharp
var hash = await Task.Run(() => ComputeHeavyHash(bytes), ct);
```
- В ASP.NET Core **не оборачивайте** I/O в `Task.Run` (`Task.Run(() => db.Query())`) — вы просто занимаете ещё один поток.
- `Task.Run` в обработчике запроса для CPU-работы тоже почти бесполезен: запрос и так на потоке пула. Смысл есть, если нужно параллельно выполнить несколько CPU-задач или разгрузить UI-поток (в десктопе).

### Параллельное ожидание: WhenAll

```csharp
// последовательно: время = сумма
var patient = await patientClient.GetAsync(id, ct);
var visits  = await visitClient.GetAsync(id, ct);
var labs    = await labClient.GetAsync(id, ct);

// параллельно: время = максимум
var patientTask = patientClient.GetAsync(id, ct);
var visitsTask  = visitClient.GetAsync(id, ct);
var labsTask    = labClient.GetAsync(id, ct);
await Task.WhenAll(patientTask, visitsTask, labsTask);
var summary = new PatientSummary(patientTask.Result, visitsTask.Result, labsTask.Result); // .Result безопасен после await WhenAll
```
Так собирает данные сборщик для печатных форм из разных storage-сервисов: независимые запросы параллельно.
> [!warning]
> Один `DbContext` нельзя использовать в параллельных запросах (`A second operation was started on this context`). Для параллели — отдельные контексты (`IDbContextFactory`) или последовательные запросы.

### Исключения в WhenAll

```csharp
var all = Task.WhenAll(t1, t2, t3);
try { await all; }
catch (Exception first)                      // await пробрасывает ПЕРВОЕ исключение
{
    var allErrors = all.Exception!.InnerExceptions;   // все исключения — в AggregateException у задачи
}
```

### WhenAny и таймауты

```csharp
var winner = await Task.WhenAny(primary.GetAsync(ct), fallback.GetAsync(ct));   // первая завершившаяся
var result = await winner;                                                      // пробросит её исключение, если было

var data = await client.GetAsync(ct).WaitAsync(TimeSpan.FromSeconds(5), ct);   // .NET 6: таймаут на ожидание

await foreach (var done in Task.WhenEach(tasks)) { Handle(await done); }       // .NET 9: по мере завершения
```

### Создание задач

- `Task.FromResult(value)`, `Task.CompletedTask` — уже завершённые (для синхронной реализации асинхронного интерфейса).
- `Task.FromException`, `Task.FromCanceled`.
- `TaskCompletionSource<T>` — вручную управляемая задача (обёртка над колбэками и событиями):
```csharp
var tcs = new TaskCompletionSource<Report>(TaskCreationOptions.RunContinuationsAsynchronously);
job.Completed += (_, r) => tcs.TrySetResult(r);
job.Failed += (_, e) => tcs.TrySetException(e);
return await tcs.Task;
```
`RunContinuationsAsynchronously` — чтобы продолжения не выполнялись синхронно в потоке, вызвавшем `SetResult` (защита от дедлоков и неожиданного реентранса).

## Нюансы и подводные камни

- «Fire-and-forget» (`_ = DoAsync();`) в веб-запросе: исключение потеряется, а scoped-сервисы будут освобождены раньше завершения задачи. Для фоновой работы — очередь и `BackgroundService`.
- `Task.WhenAll` на тысячах задач одновременно → перегрузка внешнего сервиса или БД. Ограничивайте параллелизм (SemaphoreSlim, `Parallel.ForEachAsync`).
- `Task` можно await-ить многократно, результат кэшируется. `ValueTask` — только один раз.
- `task.Result` и `task.Wait()` до завершения блокируют поток (и оборачивают исключение в AggregateException).
- `ContinueWith` — низкоуровневый и опасный API (планировщик, исключения). Используйте `await`.

## Тестирование

```csharp
[Fact]
public async Task Collects_data_in_parallel()
{
    var patients = Substitute.For<IPatientClient>();
    var visits = Substitute.For<IVisitClient>();
    patients.GetAsync(default, default).ReturnsForAnyArgs(Task.Delay(100).ContinueWith(_ => new PatientDto()));
    visits.GetAsync(default, default).ReturnsForAnyArgs(Task.Delay(100).ContinueWith(_ => (IReadOnlyList<VisitDto>)[]));
    var sw = Stopwatch.StartNew();
    await new SummaryCollector(patients, visits).CollectAsync(Guid.NewGuid(), default);
    sw.ElapsedMilliseconds.Should().BeLessThan(180);   // ~100 мс, а не 200
}
```

## Вопросы с ответами

> [!question]- Чем Task отличается от Thread?
> Thread — поток ОС. Task — абстракция асинхронной операции и её результата. I/O-задача вообще не занимает поток во время ожидания, CPU-задача выполняется на потоке пула. Task поддерживает продолжения, результат, исключения и отмену.

> [!question]- Когда использовать Task.Run?
> Для CPU-bound работы, которую нужно вынести с текущего потока (UI-поток) или распараллелить. Не для I/O и не как обёртку над синхронными вызовами в ASP.NET Core.

> [!question]- Как выполнить несколько независимых запросов параллельно?
> Запустить все задачи, не дожидаясь каждой, и затем await Task.WhenAll. Время будет равно самому долгому запросу, а не сумме.

> [!question]- Что будет с исключениями, если упали несколько задач в WhenAll?
> await пробросит первое исключение. Все исключения доступны в Exception.InnerExceptions задачи, которую вернул WhenAll.

> [!question]- Что такое TaskCompletionSource?
> Способ создать Task, которой вы управляете вручную (SetResult, SetException, SetCanceled). Используется для оборачивания колбэков и событий в async-API.

## Связанные темы

- Предыдущая: [[N:3ea33104867981e489a4deea43404757]] · Следующая: [[N:3ea33104867981e7b59cf5c1c7675837]]
- Parallel и ограничение параллелизма: [[N:3ea331048679812fa7fec502182c29d0]]
- Promise.all в JS (аналог): [[N:3ea3310486798125aed9f655f8593986]]
- Фабрика отчётов и сбор данных: [[N:3ea33104867981f697efff1f2f6a4d2f]]
- DbContext и параллельность: [[N:3ea33104867981c7a0d3ffbde71096db]]
