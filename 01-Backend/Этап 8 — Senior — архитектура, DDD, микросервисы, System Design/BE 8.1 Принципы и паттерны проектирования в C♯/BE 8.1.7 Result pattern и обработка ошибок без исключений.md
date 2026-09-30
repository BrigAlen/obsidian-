---
type: topic
domain: backend
stage: 8
section: "8.1"
order: 7
status: todo
level: senior
notion_id: 3ea33104867981a8bdded452aaea7f32
tags: [domain/backend, stage/8, level/senior, topic/design, topic/patterns, topic/errors, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Result pattern и обработка ошибок без исключений

↑ [[BE 8.1 Принципы и паттерны проектирования в C♯|8.1 Принципы и паттерны проектирования в C♯]] · ← [[BE 8.1.6 Паттерны доступа к данным — Repository, Unit of Work, Specification|Предыдущая]] · → [[BE 8.1.8 Антипаттерны и code smells|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Различие исключений и ожидаемых ошибок — признак зрелого дизайна.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Исключения для **исключительных** ситуаций (сбой БД, баг). Для **ожидаемых** исходов (не найдено, невалидные данные, конфликт) удобнее возвращать результат.

```csharp
public readonly record struct Error(string Code, string Message);

public class Result<T>
{
    public T? Value { get; }
    public Error? Error { get; }
    public bool IsSuccess => Error is null;
    private Result(T? v, Error? e) { Value = v; Error = e; }
    public static Result<T> Ok(T value) => new(value, null);
    public static Result<T> Fail(Error error) => new(default, error);
    public TOut Match<TOut>(Func<T, TOut> ok, Func<Error, TOut> fail) => IsSuccess ? ok(Value!) : fail(Error!.Value);
}

public async Task<Result<Order>> CancelAsync(Guid id, CancellationToken ct)
{
    var order = await repo.GetAsync(id, ct);
    if (order is null) return Result<Order>.Fail(new("order.not_found", "Заказ не найден"));
    if (order.Status == Status.Shipped) return Result<Order>.Fail(new("order.shipped", "Заказ уже отправлен"));
    order.Cancel();
    return Result<Order>.Ok(order);
}

// endpoint
return (await svc.CancelAsync(id, ct)).Match(o => Results.Ok(o.ToDto()), e => e.Code switch
{
    "order.not_found" => Results.NotFound(),
    _ => Results.Conflict(new ProblemDetails { Title = e.Message }),
});
```

| Подход | Плюсы | Минусы |
|---|---|---|
| Исключения | меньше кода на «счастливом» пути, стек | дорого, скрытый поток управления, забывают ловить |
| Result | ошибки видны в сигнатуре, дешёвые | многословнее |
| Discriminated union (`OneOf`, паттерн-матчинг) | выразительные варианты | библиотека |
| Кортежи/`TryXxx` | для простых случаев | |

Библиотеки: ErrorOr, FluentResults, OneOf, LanguageExt.

## Нюансы и подводные камни

- Не смешивайте стили: часть ошибок исключениями, часть Result — определите правило.
- Result не заменяет исключения для инфраструктурных сбоев.
- Игнорирование Result (`_ = await svc...`) молча теряет ошибку — используйте анализаторы.
- Исключения дороги (стек-трейс): не используйте их в горячих путях для управления потоком.

## Практика

1. Перепишите сервис на Result и сопоставьте ошибки со статус-кодами.
2. Замерьте стоимость исключений против Result в BenchmarkDotNet.
3. Введите единый каталог кодов ошибок.

## Вопросы с ответами

> [!question]- Исключения или Result?
> Исключения — для непредвиденного, Result — для ожидаемых бизнес-исходов.

> [!question]- Почему исключения для потока управления плохи?
> Они медленны, неявны в сигнатуре и усложняют чтение кода.

## Связанные темы

- [[N:3ea3310486798124917af0db2e701077]]
- [[N:3ea331048679815a8e67e0370114ed0c]]
