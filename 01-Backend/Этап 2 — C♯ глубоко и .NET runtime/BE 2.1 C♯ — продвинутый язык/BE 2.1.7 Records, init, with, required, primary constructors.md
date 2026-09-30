---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 7
status: todo
level: middle
notion_id: 3ea331048679810e866fff73c25c9cd8
tags: [domain/backend, stage/2, level/middle, topic/records, topic/types, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Records, init, with, required, primary constructors

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.6 Extension methods и fluent API|Предыдущая]] · → [[BE 2.1.8 Span и Memory — stackalloc, ref struct|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Records, `init`, `required` и primary constructors — «современный C#» в одном вопросе. Спросят, чем record отличается от class, как устроено равенство, что делает `with`, зачем `init` и `required`, чем primary constructor у record отличается от primary constructor у класса.

> [!note] Переписано
> В Notion эта страница содержала шаблонный текст без отношения к теме. Здесь — содержательная версия.

## Объяснение

### record: тип с равенством по значению
```csharp
public record Patient(Guid Id, string LastName, DateOnly BirthDate);          // record class, позиционный
public readonly record struct Money(decimal Amount, string Currency);         // record struct, иммутабельный

var a = new Patient(id, "Иванов", new(1990, 1, 1));
var b = a with { LastName = "Петров" };       // копия с изменением, оригинал не тронут
a == new Patient(id, "Иванов", new(1990, 1, 1));   // true: сравнение по значениям свойств
a.ToString();                                        // Patient { Id = ..., LastName = Иванов, BirthDate = ... }
var (i, l, d) = a;                                   // деконструкция (позиционный record)
```
Компилятор генерирует: конструктор, свойства `init`, `Equals`/`GetHashCode`, `==`/`!=`, `ToString` (`PrintMembers`), `Deconstruct`, `<Clone>$` для `with`, `EqualityContract`.
- **record class** — ссылочный тип (по умолчанию `record` = `record class`).
- **record struct** — значимый; `readonly record struct` иммутабелен, `record struct` без `readonly` имеет изменяемые свойства.
- Наследование: record наследуется только от record (`record Student(string Course) : Person(...)`); равенство учитывает точный тип.

### init и required
```csharp
public class Patient
{
    public required string LastName { get; init; }     // обязателен при создании, дальше только чтение
    public string? Phone { get; init; }
    public Guid Id { get; init; } = Guid.NewGuid();
}
var p = new Patient { LastName = "Иванова" };          // без LastName не скомпилируется
// p.LastName = "X";                                     // ошибка: init-only
```
- `init` — сеттер, который вызывается только в инициализаторе объекта, `with` и конструкторе.
- `required` (C# 11) — компилятор потребует задать член при создании, работает и без конструктора; полезно для DTO и десериализации.
- `[SetsRequiredMembers]` на конструкторе сообщает, что он задаёт все required-члены.
- `System.Text.Json` (.NET 7+) учитывает `required`: при отсутствии поля в JSON бросит исключение.

### Primary constructors (C# 12)
```csharp
public class ReportService(IDataCollector collector, ILogger<ReportService> log)   // у класса
{
    public Task<byte[]> BuildAsync(Guid id) { log.LogInformation("Build {Id}", id); return collector.CollectAsync(id); }
}
```
- **У класса и struct**: параметры — захваченные переменные (не свойства, не readonly). Доступны в теле, изменяемы.
- **У record**: параметры автоматически становятся **публичными init-свойствами** и участвуют в равенстве и деконструкции.
- Если нужен `readonly`, присвойте в поле: `private readonly IDataCollector _c = collector;`.

### Когда что использовать
| Задача | Выбор |
|---|---|
| DTO, сообщения, запросы/ответы API | `record` или `record class` |
| Value object (деньги, диапазон, идентификатор) | `readonly record struct` (мелкий) или `record` |
| Сущность с идентичностью и изменяемым состоянием (EF Core) | обычный `class` |
| Сервис с зависимостями | класс с primary constructor |
| Конфигурация, привязка из JSON | класс с `required`/`init` свойствами или record |

## Нюансы и подводные камни
- Равенство record — по значениям **всех** свойств. Для полей-коллекций сравнение идёт по ссылке, содержимое не сравнивается.
- Record с изменяемыми свойствами (`{ get; set; }`) теряет смысл: хэш-код может измениться, и объект «потеряется» в `HashSet`.
- `with` делает **поверхностную** копию: вложенные ссылочные объекты общие.
- Сущности EF Core лучше не делать record: change tracker опирается на ссылочную идентичность и `Equals` по значению создаёт неожиданности. Для проекций и DTO — самое место.
- Primary constructor класса не делает параметры полями: если использовать их в нескольких методах, компилятор захватывает в скрытое поле, и это может удивлять при рефакторинге.
- В DI primary constructor работает как обычный: параметры внедряются.

## Практика
- Переписать DTO-класс пациента на record с `required`-свойством и проверить `with`.
- Сравнить два record с `List<int>` внутри и объяснить результат.
- Создать `readonly record struct DateRange` с валидацией в конструкторе.

## Вопросы с ответами
> [!question]- Чем record отличается от class?
> Компилятор генерирует равенство по значению, `ToString`, `Deconstruct`, `with`-копирование и позиционные `init`-свойства. Record предназначен для данных, а не для сущностей с идентичностью.

> [!question]- Что делает `with`?
> Создаёт неглубокую копию record или struct с изменёнными свойствами. Оригинал не меняется.

> [!question]- Чем `init` отличается от `set` и от `readonly`?
> `init` можно вызывать только при создании объекта (инициализатор, `with`, конструктор). `set` — в любое время. `readonly`-поле — только в конструкторе и объявлении.

> [!question]- Что делает `required`?
> Заставляет компилятор требовать присвоения члена при создании объекта. Без него код не скомпилируется.

> [!question]- Чем primary constructor записи отличается от primary constructor класса?
> У record параметры становятся публичными init-свойствами и участвуют в равенстве. У class параметры — просто захваченные переменные, свойств не создаётся.

## Связанные темы
- Предыдущая: [[N:3ea33104867981efbe4bdf7ca565e0e1]] · Следующая: [[N:3ea33104867981548d57ffd75d21ec61]]
- Enum, record, tuple: [[N:3ea331048679812f9ce5e774db1a3627]]
- Equals и GetHashCode: [[N:3ea33104867981339ec6f0b777d85f83]]
- Классы и конструкторы: [[N:3ea331048679817b85dbefe554670a2e]]
- DDD: value object: [[N:3ea33104867981fdacffc2220726e99c]]
