---
type: topic
domain: backend
stage: 2
section: "2.3"
order: 7
status: todo
level: middle
notion_id: 3ea33104867981ffa016f695f07100a4
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/concurrency, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Race condition, deadlock, livelock, starvation

↑ [[BE 2.3 Асинхронность и многопоточность|2.3 Асинхронность и многопоточность]] · ← [[BE 2.3.6 Синхронизация — lock, Monitor, SemaphoreSlim, Interlocked, ReaderWriterLockSlim|Предыдущая]] · → [[BE 2.3.8 Потокобезопасные коллекции и Channels|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






























































> [!info] Зачем это на собесе
> Вопросы вида «приведи пример deadlock и как его диагностировать» задают почти всем. Нужно показать понимание условий возникновения и практических способов борьбы.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Проблема | Суть | Симптом |
|---|---|---|
| Race condition | результат зависит от порядка выполнения потоков | плавающие неверные данные, «иногда падает» |
| Data race | одновременный доступ к памяти без синхронизации, хотя бы одна запись | порча данных, torn reads |
| Deadlock | потоки ждут друг друга бесконечно | зависание, 0% CPU |
| Livelock | потоки активно уступают друг другу, но прогресса нет | высокий CPU, ничего не происходит |
| Starvation | поток годами не получает ресурс | отдельные задачи «застревают» |

### Race condition: check-then-act

```csharp
// Плохо: между проверкой и записью может вклиниться другой поток
if (!_cache.ContainsKey(key))
    _cache[key] = Load(key);

// Хорошо
var value = _concurrentCache.GetOrAdd(key, k => Load(k));
```

Обратите внимание: `GetOrAdd` с фабрикой может вызвать фабрику несколько раз. Если фабрика дорогая — храните `Lazy<T>`.

### Deadlock: четыре условия Коффмана

1. Взаимное исключение.
2. Удержание и ожидание (hold and wait).
3. Отсутствие принудительного освобождения.
4. Циклическое ожидание.

Достаточно сломать любое из них.

```csharp
// Поток A: lock(a) -> lock(b); поток B: lock(b) -> lock(a)
void Transfer(Account from, Account to)
{
    lock (from) lock (to) { /* ... */ }
}

// Исправление: единый порядок захвата
void TransferSafe(Account from, Account to)
{
    var (first, second) = from.Id < to.Id ? (from, to) : (to, from);
    lock (first) lock (second) { /* ... */ }
}
```

Отдельно — async-deadlock: блокирующий `.Result` в контексте с однопоточным SynchronizationContext (см. [[N:3ea33104867981489552e5d712d06076]]).

### Livelock и starvation

Livelock — два вежливых человека в коридоре, каждый уступает дорогу в ту же сторону; лечится случайной задержкой (jitter) или приоритетом. Starvation — несправедливые блокировки, длинные задачи, вытесняющие короткие; лечится честными очередями, лимитами и приоритетами.

## Нюансы и подводные камни

- Гонки не воспроизводятся стабильно: тестируйте стресс-тестами и с разным числом потоков.
- `Monitor.TryEnter(obj, timeout)` и `SemaphoreSlim.WaitAsync(timeout)` превращают deadlock в диагностируемую ошибку.
- Неизменяемые данные и передача сообщений (Channels, actor-подход) исключают большинство гонок.
- Диагностика: `dotnet-dump analyze` + `clrstack -all`, `dotnet-stack`, окно Parallel Stacks в Visual Studio.

## Практика

1. Напишите минимальный deadlock на двух замках, снимите dump и найдите его в `clrstack`.
2. Исправьте счётчик с `x++` из 8 потоков через `Interlocked`.
3. Сымитируйте starvation: длинные задачи в ThreadPool и короткая, которая не выполняется.

## Вопросы с ответами

> [!question]- Чем race condition отличается от data race?
> Data race — низкоуровневое: конфликтующие обращения к памяти без синхронизации. Race condition — логическая ошибка порядка, она возможна и без data race (например, атомарные операции, но неверная последовательность).

> [!question]- Как предотвратить deadlock?
> Единый порядок захвата, таймауты, минимальная область замка, отказ от вложенных замков, использование неблокирующих структур и передачи сообщений.

> [!question]- Как найти deadlock в проде?
> Снять dump процесса (`dotnet-dump collect`), посмотреть стеки всех потоков и цепочку ожидания замков; в Visual Studio — Parallel Stacks и Threads.

> [!question]- Что такое thread-safe и reentrant?
> Thread-safe — корректная работа при одновременном вызове из нескольких потоков. Reentrant — безопасный повторный вход из того же потока или в прерванном состоянии; это разные свойства.

## Связанные темы

- [[N:3ea33104867981fea69fce768dc3e0dd]]
- [[N:3ea331048679817e96d8c67b432324e0]]
