---
type: topic
domain: backend
stage: 2
section: "2.3"
order: 9
status: todo
level: middle
notion_id: 3ea331048679812fa7fec502182c29d0
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/concurrency, topic/tpl, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Parallel, PLINQ, Task.WhenAll и ограничение параллелизма

↑ [[BE 2.3 Асинхронность и многопоточность|2.3 Асинхронность и многопоточность]] · ← [[BE 2.3.8 Потокобезопасные коллекции и Channels|Предыдущая]] · → [[BE 2.3.10 Антипаттерны — async void, .Result, sync over async|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->































> [!info] Зачем это на собесе
> Часто просят распараллелить обработку списка и ограничить число одновременных запросов. Важно понимать разницу между CPU-bound и I/O-bound.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Задача | Инструмент |
|---|---|
| CPU-bound над коллекцией | `Parallel.For/ForEach`, PLINQ |
| I/O-bound (HTTP, БД) | `Task.WhenAll`, `Parallel.ForEachAsync` |
| Ограничить одновременность | `SemaphoreSlim`, `MaxDegreeOfParallelism`, `Channel` |

### Parallel и PLINQ

```csharp
Parallel.For(0, images.Length, i => Resize(images[i]));

var sum = numbers.AsParallel().Where(IsPrime).Sum();
```

Они делят работу между потоками ThreadPool и подходят для вычислений. Не применяйте их для I/O: потоки будут заблокированы впустую.

### Task.WhenAll

```csharp
var tasks = urls.Select(u => http.GetStringAsync(u));
string[] pages = await Task.WhenAll(tasks);
```

`WhenAll` ждёт все задачи. При ошибке `await` пробросит только первое исключение, остальные лежат в `task.Exception.InnerExceptions`.

### Parallel.ForEachAsync (.NET 6+)

```csharp
await Parallel.ForEachAsync(urls,
    new ParallelOptions { MaxDegreeOfParallelism = 8, CancellationToken = ct },
    async (url, token) =>
    {
        var html = await http.GetStringAsync(url, token);
        await store.SaveAsync(url, html, token);
    });
```

### Ручное ограничение

```csharp
var gate = new SemaphoreSlim(5);
var tasks = urls.Select(async u =>
{
    await gate.WaitAsync(ct);
    try { return await http.GetStringAsync(u, ct); }
    finally { gate.Release(); }
});
var results = await Task.WhenAll(tasks);
```

## Нюансы и подводные камни

- Запуск 10 000 задач без ограничения «положит» внешний сервис или исчерпает соединения; всегда ограничивайте.
- `Parallel.ForEach` с async-лямбдой — ошибка: лямбда становится `async void`, вызов не ждёт задач. Используйте `ForEachAsync`.
- PLINQ не гарантирует порядок без `AsOrdered()`.
- Общее состояние в параллельных циклах — источник гонок; агрегируйте локально и объединяйте в конце (`localInit/localFinally`).
- Число потоков ThreadPool ограничено: большое число блокирующих задач вызывает thread starvation.

## Практика

1. Обработать 1000 URL с лимитом 10 одновременных запросов тремя способами и сравнить.
2. Посчитать простые числа последовательно, через `Parallel.For` и PLINQ, замерить.
3. Собрать результаты `WhenAll` и корректно обработать частичные ошибки.

## Вопросы с ответами

> [!question]- Когда Parallel, а когда Task.WhenAll?
> `Parallel` — для CPU-bound, он занимает потоки. `Task.WhenAll` — для I/O-bound, потоки не блокируются на ожидании.

> [!question]- Как ограничить число одновременных async-операций?
> `SemaphoreSlim`, `Parallel.ForEachAsync` с `MaxDegreeOfParallelism`, либо `Channel` с фиксированным числом консюмеров.

> [!question]- Что случится, если одна из задач в WhenAll упадёт?
> `WhenAll` дождётся всех задач; `await` выбросит первое исключение, остальные доступны через `Exception.InnerExceptions` у самой задачи `WhenAll`.

## Связанные темы

- [[N:3ea331048679817e96d8c67b432324e0]]
- [[N:3ea33104867981489552e5d712d06076]]
