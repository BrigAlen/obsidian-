---
type: topic
domain: backend
stage: 1
section: "1.3"
order: 7
status: todo
level: junior
notion_id: 3ea3310486798167aae3ed222aeb634e
tags: [domain/backend, stage/1, level/junior, topic/exceptions, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Исключения: try, catch, finally, when, свои исключения

↑ [[BE 1.3 C♯ — основы языка|1.3 C♯: основы языка]] · ← [[BE 1.3.6 Методы и параметры — ref, out, in, params, именованные аргументы|Предыдущая]] · → [[BE 1.3.8 Enum, record, tuple, деконструкция|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->



























> [!info] Зачем это на собесе
> правильная обработка ошибок отличает надёжный сервис. Спросят про иерархию исключений, `throw` vs `throw ex`, фильтры `when`, стоимость исключений и когда их не использовать.

## Объяснение

### Иерархия

- `System.Exception` — база.
- `SystemException`: `NullReferenceException`, `InvalidOperationException`, `ArgumentException` (+ `ArgumentNullException`, `ArgumentOutOfRangeException`), `FormatException`, `KeyNotFoundException`, `OperationCanceledException` (+ `TaskCanceledException`), `TimeoutException`, `IOException`, `HttpRequestException`.
- Свои исключения наследуют от `Exception` (не от `ApplicationException`).

### try / catch / finally

```csharp
try
{
    var data = await collector.CollectAsync(patientId, ct);
    return reportFactory.Create(type).Render(data);
}
catch (OperationCanceledException) when (ct.IsCancellationRequested)
{
    throw;                                            // отмена клиентом — не ошибка, пробрасываем
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)   // фильтр исключений
{
    throw new PatientNotFoundException(patientId, ex);  // оборачиваем с InnerException
}
catch (Exception ex)
{
    _log.LogError(ex, "Report generation failed for {PatientId}", patientId);
    throw;
}
finally
{
    stopwatch.Stop();                                 // выполнится всегда
}
```
- Порядок `catch` — от частного к общему.
- **Фильтр `when`** проверяется **до** раскрутки стека. Не пойманное исключение сохраняет исходный стек, а фильтр можно использовать для логирования без перехвата: `catch (Exception ex) when (Log(ex)) {}` с `Log`, возвращающим false.

### throw; vs throw ex;

```csharp
catch (Exception ex)
{
    throw;       //  сохраняет исходный стектрейс
    // throw ex; //  стектрейс начинается отсюда — теряем, где реально упало
}
```
Для проброса из другого контекста: `ExceptionDispatchInfo.Capture(ex).Throw()`.

### Свои исключения

```csharp
public sealed class PatientNotFoundException(Guid patientId, Exception? inner = null)
    : Exception($"Patient {patientId} not found", inner)
{
    public Guid PatientId { get; } = patientId;
}
```
Добавляйте данные для диагностики, передавайте `inner`. Доменные исключения потом маппятся в HTTP-статусы глобальным обработчиком (`PatientNotFoundException` → 404).

### using и освобождение ресурсов

`using` — синтаксический сахар над `try/finally { Dispose() }`:
```csharp
await using var conn = await dataSource.OpenConnectionAsync(ct);
using var stream = new MemoryStream();
```

### Исключения и производительность

Выброс исключения дорогой (сбор стектрейса, раскрутка стека): микросекунды против наносекунд обычного return. Правило:
- исключения — для **исключительных** ситуаций (нарушение контракта, недоступна БД);
- ожидаемые исходы (валидация пользовательского ввода, «не найдено» в поиске) — через `TryXxx`, `bool`, `null` или **Result pattern**.

### Где ловить

- Не ловить «на всякий случай» в каждом методе.
- Ловить там, где можно **что-то сделать**: повторить, преобразовать в доменную ошибку, добавить контекст, освободить ресурс.
- Всё остальное — в **глобальном обработчике** (`IExceptionHandler` / middleware), который логирует и возвращает ProblemDetails.

## Нюансы и подводные камни

- Пустой `catch {}` глотает ошибку — худший антипаттерн.
- `catch (Exception)` вокруг `await` перехватит и `OperationCanceledException`: отмену обрабатывайте отдельно.
- Исключение в `finally` заменит исходное.
- В `async void` исключение не перехватить снаружи, оно роняет процесс.
- Необработанное исключение в `BackgroundService` в .NET 8+ по умолчанию **останавливает хост** (`BackgroundServiceExceptionBehavior.StopHost`).
- `StackOverflowException` и `OutOfMemoryException` (в общем случае) не перехватываются осмысленно.

## Тестирование

```csharp
[Fact]
public async Task Throws_when_patient_missing()
{
    var act = () => service.GetAsync(Guid.NewGuid(), CancellationToken.None);
    await act.Should().ThrowAsync<PatientNotFoundException>()
        .Where(e => e.PatientId != Guid.Empty);
}
```

## Вопросы с ответами

> [!question]- Чем throw отличается от throw ex?
> throw сохраняет исходный стектрейс. throw ex сбрасывает его на текущую строку, и теряется место, где на самом деле произошла ошибка.

> [!question]- Что такое фильтры исключений (when) и чем они лучше if внутри catch?
> Условие проверяется до раскрутки стека. Если оно ложно, исключение не считается пойманным и идёт дальше с неизменённым стеком. Удобно для выборочной обработки и логирования.

> [!question]- Когда использовать исключения, а когда Result или Try-паттерн?
> Исключения — для неожиданных ситуаций и нарушения контрактов. Для ожидаемых исходов (валидация, «не найдено», бизнес-отказ) — Result, bool TryXxx или null: это дешевле и явнее в сигнатуре.

> [!question]- Выполнится ли finally, если в try есть return?
> Да, finally выполняется при return, break, continue и исключении. Не выполнится только при аварийном завершении процесса (Environment.FailFast, StackOverflow, kill).

> [!question]- Как организовать обработку ошибок в Web API?
> Доменные исключения или Result в бизнес-слое. Глобальный IExceptionHandler, который логирует и маппит исключения в ProblemDetails со статусами (404, 409, 422, 500). Без утечки деталей в проде.

## Связанные темы

- Предыдущая: [[N:3ea33104867981fab5abd8e186ca973d]] · Следующая: [[N:3ea331048679812f9ce5e774db1a3627]]
- Глобальная обработка ошибок: [[N:3ea33104867981469ec0c25216311408]]
- Result pattern: [[N:3ea33104867981a8bdded452aaea7f32]]
- IDisposable: [[N:3ea33104867981dcbbedd3d78a7442c0]]
- Ошибки в JS: [[N:3ea331048679816da10fe17794cbb365]]
- async void: [[N:3ea33104867981489552e5d712d06076]]
