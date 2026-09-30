---
type: topic
domain: backend
stage: 2
section: "2.3"
order: 8
status: todo
level: middle
notion_id: 3ea331048679817e96d8c67b432324e0
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/concurrency, topic/collections, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Потокобезопасные коллекции и Channels

↑ [[BE 2.3 Асинхронность и многопоточность|2.3 Асинхронность и многопоточность]] · ← [[BE 2.3.7 Race condition, deadlock, livelock, starvation|Предыдущая]] · → [[BE 2.3.9 Parallel, PLINQ, Task.WhenAll и ограничение параллелизма|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

















































> [!info] Зачем это на собесе
> Спрашивают, какую коллекцию выбрать для очереди задач или кэша и чем Channel лучше BlockingCollection.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### System.Collections.Concurrent

| Тип | Назначение | Замечание |
|---|---|---|
| `ConcurrentDictionary<K,V>` | кэш, реестр | `GetOrAdd`/`AddOrUpdate` атомарны, но фабрики могут выполниться несколько раз |
| `ConcurrentQueue<T>` | FIFO, lock-free | нет блокирующего ожидания |
| `ConcurrentStack<T>` | LIFO | |
| `ConcurrentBag<T>` | неупорядоченный пул, оптимален когда продюсер = консюмер | сложнее в отладке |
| `BlockingCollection<T>` | блокирующая очередь producer/consumer | блокирует потоки, не async |
| `ImmutableArray/ImmutableDictionary` | копирование при записи, безопасное чтение | подходит для конфигураций |

### Channel\<T\>

Асинхронная очередь producer/consumer из `System.Threading.Channels`.

```csharp
var channel = Channel.CreateBounded<Job>(new BoundedChannelOptions(100)
{
    FullMode = BoundedChannelFullMode.Wait,
    SingleReader = false,
    SingleWriter = false,
});

// Продюсер
async Task ProduceAsync(IEnumerable<Job> jobs, CancellationToken ct)
{
    foreach (var j in jobs)
        await channel.Writer.WriteAsync(j, ct); // ждёт, если канал полон
    channel.Writer.Complete();
}

// Консюмеры
async Task ConsumeAsync(CancellationToken ct)
{
    await foreach (var job in channel.Reader.ReadAllAsync(ct))
        await job.RunAsync(ct);
}

await Task.WhenAll(
    ProduceAsync(source, ct),
    ConsumeAsync(ct), ConsumeAsync(ct), ConsumeAsync(ct));
```

Ограниченный (bounded) канал даёт backpressure: медленные потребители тормозят производителя, память не растёт бесконечно. Unbounded канал безопаснее только если поток данных заведомо мал.

## Нюансы и подводные камни

- `ConcurrentDictionary` потокобезопасен для отдельных операций, но составные («прочитал — проверил — записал») не атомарны.
- Перечисление `ConcurrentDictionary` даёт снимок без гарантии согласованности.
- Не забывайте `Writer.Complete()`, иначе читатели будут ждать вечно.
- В `Channel` выбирайте `FullMode` осознанно: `Wait`, `DropOldest`, `DropNewest`, `DropWrite`.
- `SingleReader/SingleWriter = true` включает более быстрые реализации, но нарушение контракта приводит к ошибкам.

## Практика

1. Построить конвейер «читаем файлы → парсим → пишем в БД» на трёх каналах.
2. Заменить `BlockingCollection` в фоновом воркере на `Channel` и сравнить использование потоков.
3. Реализовать кэш на `ConcurrentDictionary<string, Lazy<Task<T>>>`, чтобы дорогая загрузка выполнялась один раз.

## Вопросы с ответами

> [!question]- Чем Channel лучше BlockingCollection?
> Channel полностью асинхронный (не блокирует потоки), поддерживает bounded/unbounded, `CancellationToken` и `IAsyncEnumerable`, быстрее на типичных нагрузках.

> [!question]- Почему в ConcurrentDictionary.GetOrAdd фабрика может вызваться дважды?
> Пока один поток вычисляет значение, другой может тоже не найти ключ и вызвать фабрику; в словарь попадёт только одно значение. Для однократности используют `Lazy<T>`.

> [!question]- Что такое backpressure?
> Механизм, при котором потребитель сообщает производителю о перегрузке. В Channel это ограниченная ёмкость и `WriteAsync`, который ждёт свободного места.

## Связанные темы

- [[N:3ea33104867981fea69fce768dc3e0dd]]
- [[N:3ea331048679812fa7fec502182c29d0]]
