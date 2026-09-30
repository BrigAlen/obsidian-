---
type: topic
domain: backend
stage: 2
section: "2.3"
order: 10
status: todo
level: middle
notion_id: 3ea33104867981489552e5d712d06076
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/async, topic/antipatterns, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Антипаттерны: async void, .Result, sync over async

↑ [[BE 2.3 Асинхронность и многопоточность|2.3 Асинхронность и многопоточность]] · ← [[BE 2.3.9 Parallel, PLINQ, Task.WhenAll и ограничение параллелизма|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




































> [!info] Зачем это на собесе
> Практически обязательный вопрос: «что не так в этом async-коде». Нужно быстро узнавать deadlock от `.Result` и `async void`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Антипаттерн | Чем плох | Как правильно |
|---|---|---|
| `async void` | исключения не перехватить, нельзя дождаться, крэш процесса | `async Task`; `async void` только для обработчиков событий |
| `.Result`, `.Wait()`, `.GetAwaiter().GetResult()` | блокирует поток, риск deadlock | `await` по всей цепочке |
| sync over async | блокирующий вызов async-метода в sync-коде | сделать вызывающий код асинхронным |
| async over sync (`Task.Run` вокруг синхронного I/O) | иллюзия асинхронности, занимает поток пула | настоящий async API |
| Fire-and-forget без обработки | потерянные исключения | фоновый сервис, `Channel`, логирование в continuation |
| Отсутствие `CancellationToken` | нельзя отменить, висящие запросы | пробрасывать токен во все async-методы |
| `await` в цикле там, где допустим параллелизм | лишняя последовательность | `Task.WhenAll` с ограничением |
| `Task.Run` в ASP.NET-обработчике | лишнее переключение, нет выигрыша | вызывать async напрямую |

### Deadlock от .Result

```csharp
// UI или классический ASP.NET с SynchronizationContext
public string Load() => LoadAsync().Result; // deadlock

async Task<string> LoadAsync()
{
    await Task.Delay(100);   // продолжение хочет вернуться в UI-поток
    return "ok";             // а он заблокирован на .Result
}
```

В ASP.NET Core SynchronizationContext нет, поэтому классического deadlock не будет, но останется блокировка потока пула и рост latency (thread starvation).

### async void

```csharp
// Плохо: исключение уронит процесс, дождаться нельзя
async void SaveAsync() { await repo.SaveAsync(); }

// Хорошо
async Task SaveAsync() { await repo.SaveAsync(); }
```

### ConfigureAwait(false)

В библиотечном коде `ConfigureAwait(false)` отвязывает продолжение от контекста и снижает риск deadlock; в ASP.NET Core приложении он не нужен.

## Нюансы и подводные камни

- `async` без `await` — предупреждение компилятора; метод выполняется синхронно.
- Возврат `Task` без `async` (elision) экономит state machine, но меняет обработку исключений и время жизни `using`.
- `Task.Run(() => asyncMethod().Wait())` — не решение, а ещё один способ занять поток.
- Проверьте `async` лямбды в LINQ (`Select(async x => ...)`): получаете `IEnumerable<Task>`, а не результаты.

## Практика

1. Воспроизведите deadlock на WinForms/WPF-примере с `.Result` и исправьте.
2. Найдите в своём проекте `.Result`, `.Wait()` и `async void`, замените.
3. Подключите анализаторы (`Microsoft.VisualStudio.Threading.Analyzers`, правила CA2007, CA2012) и посмотрите предупреждения.

## Вопросы с ответами

> [!question]- Почему async void опасен?
> Нет `Task`, поэтому вызывающий не может дождаться завершения или поймать исключение; необработанное исключение уходит в SynchronizationContext и роняет процесс. Допустим только для обработчиков событий.

> [!question]- Почему .Result вызывает deadlock?
> Поток удерживает контекст и блокируется, а продолжение метода после `await` ждёт возврата в этот же контекст. Ни один не может продвинуться.

> [!question]- Нужен ли ConfigureAwait(false) в ASP.NET Core?
> В самом приложении нет (контекста синхронизации нет), в переиспользуемых библиотеках — желателен.

> [!question]- Как правильно запускать фоновую работу?
> `BackgroundService`/`IHostedService`, очередь на `Channel`, а не голый fire-and-forget.

## Связанные темы

- [[N:3ea33104867981fea69fce768dc3e0dd]]
- [[N:3ea331048679812fa7fec502182c29d0]]
