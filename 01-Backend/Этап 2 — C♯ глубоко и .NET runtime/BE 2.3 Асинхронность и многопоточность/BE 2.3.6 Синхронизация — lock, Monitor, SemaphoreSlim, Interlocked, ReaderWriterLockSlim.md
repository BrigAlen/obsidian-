---
type: topic
domain: backend
stage: 2
section: "2.3"
order: 6
status: todo
level: middle
notion_id: 3ea33104867981fea69fce768dc3e0dd
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/concurrency, priority/must]
reviewed:
next_review:
priority: must
time: 8
---

# Синхронизация: lock, Monitor, SemaphoreSlim, Interlocked, ReaderWriterLockSlim

↑ [[BE 2.3 Асинхронность и многопоточность|2.3 Асинхронность и многопоточность]] · ← [[BE 2.3.5 CancellationToken и таймауты|Предыдущая]] · → [[BE 2.3.7 Race condition, deadlock, livelock, starvation|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















































> [!info] Зачем это на собесе
> Классика: «как защитить общий ресурс», «чем lock отличается от SemaphoreSlim», «почему нельзя await внутри lock». Отвечать нужно с примерами и с оговорками по производительности.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Синхронизация нужна, когда несколько потоков читают и меняют одно и то же состояние. Без неё возникают гонки данных (см. [[N:3ea33104867981ffa016f695f07100a4]]).

| Примитив | Когда использовать | Async-friendly | Заметка |
|---|---|---|---|
| `lock` / `Monitor` | короткая критическая секция в одном процессе | нет | самый дешёвый; `lock` = `Monitor.Enter/Exit` + try/finally |
| `Interlocked` | атомарные операции над int/long/ссылкой | да (не блокирует) | `Increment`, `Add`, `CompareExchange`, `Exchange` |
| `SemaphoreSlim` | ограничить число одновременных входов; критическая секция с `await` | да (`WaitAsync`) | не reentrant |
| `ReaderWriterLockSlim` | много чтений, редкие записи | нет | есть upgradeable-режим, легко словить deadlock |
| `Mutex` | синхронизация между процессами | нет | тяжёлый, ядро ОС |
| `ManualResetEventSlim`, `CountdownEvent`, `Barrier` | сигналы и координация | частично | для сценариев «дождись события» |

### lock

```csharp
private readonly object _gate = new();
private int _balance;

public void Deposit(int amount)
{
    lock (_gate)
    {
        _balance += amount;
    }
}
```

Блокируемся на приватном `readonly` объекте, а не на `this`, `typeof(T)` или строке: их может захватить чужой код. В .NET 9 появился тип `System.Threading.Lock` — `lock` на нём быстрее и явнее.

### Interlocked

```csharp
private long _requests;
public void OnRequest() => Interlocked.Increment(ref _requests);

// lock-free обновление по CAS
static void AddIfLess(ref int target, int value, int max)
{
    int current, next;
    do
    {
        current = Volatile.Read(ref target);
        next = Math.Min(current + value, max);
    } while (Interlocked.CompareExchange(ref target, next, current) != current);
}
```

### SemaphoreSlim

```csharp
private readonly SemaphoreSlim _sem = new(initialCount: 1, maxCount: 1);

public async Task UpdateAsync()
{
    await _sem.WaitAsync();
    try
    {
        await _repo.SaveAsync(); // await внутри допустим
    }
    finally
    {
        _sem.Release();
    }
}
```

С `initialCount: N` получаем ограничитель параллелизма (например, не более 5 одновременных HTTP-запросов).

### ReaderWriterLockSlim

```csharp
private readonly ReaderWriterLockSlim _rw = new();
private readonly Dictionary<string, string> _cache = new();

public string? Get(string k)
{
    _rw.EnterReadLock();
    try { return _cache.GetValueOrDefault(k); }
    finally { _rw.ExitReadLock(); }
}

public void Set(string k, string v)
{
    _rw.EnterWriteLock();
    try { _cache[k] = v; }
    finally { _rw.ExitWriteLock(); }
}
```

Выигрыш есть только при заметном перекосе в сторону чтений и длинных критических секциях; иначе обычный `lock` быстрее.

## Нюансы и подводные камни

- Нельзя писать `await` внутри `lock` — код не компилируется; после `await` продолжение может пойти в другом потоке, а Monitor привязан к потоку. Используйте `SemaphoreSlim`.
- `lock` реентерабелен (тот же поток может зайти повторно), `SemaphoreSlim` — нет: повторный `WaitAsync` в том же потоке зависнет.
- Всегда `Release` в `finally`, иначе одна исключительная ситуация блокирует всех навсегда.
- Держите критическую секцию короткой: не вызывайте внешний код, I/O и виртуальные методы под замком.
- Единый порядок захвата нескольких замков — защита от deadlock.
- `volatile` даёт видимость записи, но не атомарность составных операций (`x++`).

## Практика

1. Реализуйте потокобезопасный счётчик тремя способами (lock, Interlocked, SemaphoreSlim) и сравните время на 10 млн операций через BenchmarkDotNet.
2. Сделайте ограничитель: не более 3 одновременных вызовов внешнего API через `SemaphoreSlim`.
3. Найдите и исправьте deadlock из двух замков, захватываемых в разном порядке.

## Вопросы с ответами

> [!question]- Чем lock отличается от SemaphoreSlim?
> `lock` — эксклюзивный, реентерабельный, привязан к потоку, не поддерживает `await`. `SemaphoreSlim` — счётчик разрешений, не реентерабельный, не привязан к потоку и имеет `WaitAsync`, поэтому подходит для async-кода и для ограничения параллелизма.

> [!question]- Почему нельзя lock(this) или lock(typeof(T))?
> Объект публично доступен: внешний код может взять тот же замок и вызвать deadlock либо ненужную конкуренцию. Нужен приватный выделенный объект.

> [!question]- Что делает Interlocked.CompareExchange?
> Атомарно сравнивает значение с ожидаемым и при совпадении заменяет на новое, возвращая прежнее. На нём строятся lock-free структуры: цикл «прочитал — посчитал — попробовал записать».

> [!question]- Когда ReaderWriterLockSlim лучше lock?
> Когда читателей намного больше, чем писателей, и чтение достаточно долгое. При коротких секциях накладные расходы RWLS выше выгоды.

> [!question]- Что такое Monitor.Wait/Pulse?
> Условная синхронизация: поток отпускает замок и ждёт сигнала `Pulse/PulseAll` от другого. Сегодня чаще используют `Channel`, `BlockingCollection` или `SemaphoreSlim`.

## Связанные темы

- [[N:3ea33104867981ffa016f695f07100a4]]
- [[N:3ea331048679817e96d8c67b432324e0]]
