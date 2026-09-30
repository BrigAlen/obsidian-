---
type: topic
domain: backend
stage: 1
section: "1.5"
order: 3
status: todo
level: junior
notion_id: 3ea3310486798119a28cdce7837acb7f
tags: [domain/backend, stage/1, level/junior, topic/generics, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Generics: обобщённые типы и методы

↑ [[BE 1.5 Коллекции и основы LINQ|1.5 Коллекции и основы LINQ]] · ← [[BE 1.5.2 Интерфейсы коллекций — IEnumerable, ICollection, IList, IReadOnly|Предыдущая]] · → [[BE 1.5.4 LINQ — основные операторы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->




































> [!info] Зачем это на собесе
> generics — основа типобезопасного переиспользуемого кода: репозитории, Result\<T\>, обобщённые хендлеры, клиенты. Здесь база, а продвинутое (вариантность, static abstract) — во 2-м этапе.

## Объяснение

### Обобщённые типы

```csharp
public sealed class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }
    private Result(bool ok, T? value, string? error) => (IsSuccess, Value, Error) = (ok, value, error);
    public static Result<T> Ok(T value) => new(true, value, null);
    public static Result<T> Fail(string error) => new(false, default, error);
}

Result<PatientDto> r = Result<PatientDto>.Ok(dto);
```
Без generics пришлось бы использовать `object`: потеря типобезопасности, приведения и boxing для value types.

### Обобщённые методы и вывод типов

```csharp
public static T Require<T>(T? value, string name) where T : class =>
    value ?? throw new ArgumentNullException(name);

var patient = Require(found, nameof(found));   // T выведен компилятором
```

### Ограничения (constraints)

```csharp
public interface IEntity { Guid Id { get; } }

public class Repository<T>(DbContext db) where T : class, IEntity   // ссылочный тип и реализует IEntity
{
    public Task<T?> GetAsync(Guid id, CancellationToken ct) =>
        db.Set<T>().FirstOrDefaultAsync(e => e.Id == id, ct);
}
```
- `where T : class` / `class?` — ссылочный тип.
- `where T : struct` — значимый тип (не nullable).
- `where T : notnull` — не допускающий null.
- `where T : new()` — есть публичный конструктор без параметров.
- `where T : BaseType`, `where T : IInterface`.
- `where T : unmanaged` — без ссылок внутри (для низкоуровневой работы с памятью).
- `where T : Enum`, `where T : Delegate`.

### Как generics работают в CLR

- Для **value types** JIT создаёт **отдельный машинный код** для каждого типа (`List<int>`, `List<double>`): без боксинга, максимальная скорость.
- Для **reference types** код **общий** (все ссылки одного размера).
- В отличие от Java, generics в .NET **не стираются**: тип доступен в рантайме (`typeof(T)`, рефлексия).

### default(T)

```csharp
T? FirstOrNothing<T>(IEnumerable<T> items) => items.Any() ? items.First() : default;   // null или 0
```

### Статические поля в generic-типе

У каждого закрытого типа свои: `Cache<Patient>.Items` и `Cache<Encounter>.Items` — разные. Иногда это используют как типизированный кэш.

### Generic-интерфейсы в DI

```csharp
public interface IHandler<TRequest, TResponse> { Task<TResponse> HandleAsync(TRequest req, CancellationToken ct); }
builder.Services.AddScoped(typeof(IRepository<>), typeof(EfRepository<>));   // открытый generic
```

## Нюансы и подводные камни

- Generic-репозиторий «на всё» часто становится бесполезной обёрткой над `DbSet`: специфичные запросы всё равно пишут отдельно.
- `List<Derived>` нельзя присвоить `List<Base>` (инвариантность), а `IEnumerable<Derived>` в `IEnumerable<Base>` — можно (ковариантность). Подробнее — во втором этапе.
- Сравнение значений типа T через `==` не компилируется без ограничений. Используйте `EqualityComparer<T>.Default.Equals(a, b)`.
- Слишком общие generic-API с кучей параметров типов трудно читать. Generics — для реального переиспользования.

## Тестирование

```csharp
[Fact]
public void Result_holds_value_on_success()
{
    var r = Result<int>.Ok(42);
    r.IsSuccess.Should().BeTrue();
    r.Value.Should().Be(42);
}
```

## Вопросы с ответами

> [!question]- Зачем нужны generics?
> Типобезопасное переиспользование кода для разных типов без приведений и боксинга. Ошибки типов ловятся компилятором.

> [!question]- Какие ограничения можно наложить на параметр типа?
> class, struct, notnull, unmanaged, new(), базовый класс, интерфейс, Enum, Delegate и их комбинации.

> [!question]- Чем generics в .NET отличаются от Java?
> В .NET они реифицированы: информация о типе есть в рантайме, для value types генерируется отдельный код без боксинга. В Java типы стираются при компиляции.

> [!question]- Что вернёт default(T)?
> null для ссылочных типов, нулевое значение для значимых (0, false, структура с нулевыми полями).

## Связанные темы

- Предыдущая: [[N:3ea331048679815d9264f038e53fd95e]] · Следующая: [[N:3ea33104867981b1aae2edc717e3332c]]
- Generics глубоко: [[N:3ea33104867981d085d7ec58153f8c7b]]
- Result pattern: [[N:3ea33104867981a8bdded452aaea7f32]]
- Repository поверх EF: [[N:3ea33104867981048155ce6c5ea28bef]]
- Generics в TypeScript: [[N:3ea331048679812d9621f339f8175cdd]]
