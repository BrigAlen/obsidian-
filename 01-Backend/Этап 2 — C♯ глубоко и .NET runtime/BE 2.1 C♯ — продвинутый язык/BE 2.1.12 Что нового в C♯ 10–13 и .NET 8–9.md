---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 12
status: todo
level: middle
notion_id: 3ea331048679811a82c2d9502acd1026
tags: [domain/backend, stage/2, level/middle, topic/csharp, topic/dotnet, topic/news, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Что нового в C# 10–13 и .NET 8–9

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.11 Сериализация — System.Text.Json и Newtonsoft|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Интервьюеры проверяют, следите ли вы за платформой: знаете ли современный синтаксис и что изменилось в .NET. Ждут не перечисления всех фич, а понимания, какие из них меняют повседневный код и где вы их применяли.

> [!note] Переписано
> В Notion эта страница содержала шаблонный текст без отношения к теме. Здесь — содержательная версия. Версии: C# 10 (.NET 6), 11 (.NET 7), 12 (.NET 8), 13 (.NET 9), 14 (.NET 10).

## Объяснение

### C# 10 (.NET 6)
- **File-scoped namespaces**: `namespace App.Domain;` без лишнего уровня отступа.
- **Global usings** и `ImplicitUsings` в проекте.
- **`record struct`**, улучшения лямбд (естественный тип, атрибуты, `static`).
- Константные интерполированные строки, `with` для структур и анонимных типов.

### C# 11 (.NET 7)
- **Raw string literals**: `"""..."""` — многострочные строки без экранирования (SQL, JSON).
- **`required`** члены, **list patterns** (`[first, .., last]`), **generic math** (`static abstract` в интерфейсах).
- `file`-модификатор доступа, `UTF-8` литералы (`"text"u8`), `scoped ref`, generic-атрибуты.

### C# 12 (.NET 8)
- **Primary constructors** для классов и структур.
- **Collection expressions**: `int[] a = [1, 2, 3];`, spread `[..a, 4]`.
- Параметры по умолчанию в лямбдах, `using` alias для любых типов, inline arrays, `[Experimental]`.

### C# 13 (.NET 9)
- **`params` для коллекций и Span**: `void Log(params ReadOnlySpan<string> parts)` без аллокации массива.
- Новый тип **`System.Threading.Lock`** и `lock` на нём.
- `\e` escape, `ref`/`unsafe` в async и итераторах, `allows ref struct`.

### C# 14 (.NET 10, LTS)
- **`field`** в свойствах: доступ к автогенерируемому полю без явной декларации.
- **Extension members**: extension-свойства и статические extension-члены.
- Null-conditional присваивание: `obj?.Prop = value;`.

### .NET 8 (LTS)
- **`FrozenDictionary`/`FrozenSet`** — неизменяемые коллекции с быстрым чтением.
- **`TimeProvider`** — абстракция времени для тестов.
- **Keyed services** в DI (`[FromKeyedServices("key")]`).
- Native AOT для ASP.NET Core (Minimal API), улучшения GC и JIT (dynamic PGO по умолчанию).
- `SearchValues<T>`, `[GeneratedRegex]`, System.Text.Json: улучшения source generation.

### .NET 9 (STS)
- **LINQ**: `CountBy`, `AggregateBy`, `Index`.
- **`HybridCache`** — двухуровневый кэш (память + распределённый) с защитой от cache stampede.
- Встроенная поддержка OpenAPI-документов (`Microsoft.AspNetCore.OpenApi`), `TypedResults`, улучшения Minimal API.
- **`Task.WhenEach`**, `OrderedDictionary<K,V>`, `System.Threading.Lock`.
- Улучшения производительности JIT/GC, `Base64Url`, `Span`-варианты API.

### .NET 10 (LTS)
- LINQ `LeftJoin`/`RightJoin`, операторы `IAsyncEnumerable` в BCL.
- Улучшения ASP.NET Core (валидация в Minimal API, SSE через `TypedResults.ServerSentEvents`), Native AOT.
- Поддержка сроком 3 года.

### Что применять в коде уже сегодня
```csharp
namespace App.Reports;                                      // file-scoped

public sealed class ReportService(IDataCollector c, TimeProvider clock, ILogger<ReportService> log)   // primary ctor + TimeProvider
{
    public required string Name { get; init; }              // required
    private static readonly int[] Sizes = [10, 20, 50];     // collection expression

    public string Describe(object x) => x switch            // pattern matching
    {
        [var first, .., var last] => $"{first}…{last}",     // list pattern
        _ => x.ToString() ?? "",
    };

    private const string Sql = """
        SELECT * FROM "Patients" WHERE "Id" = @id
        """;                                                 // raw string
}
```

## Нюансы и подводные камни
- Версия языка привязана к TFM: C# 13 из коробки в .NET 9 SDK; для старого таргета нужен `<LangVersion>`, и не все фичи требуют рантайма.
- STS-релизы (.NET 9) поддерживаются 18 месяцев, LTS (8, 10) — 3 года: для продакшена обычно LTS.
- Переход на новую версию — ревью breaking changes (поведение `System.Text.Json`, DI, EF Core).
- Не «переписывайте всё на новый синтаксис» ради синтаксиса: применяйте там, где код становится короче и яснее.

## Практика
- Прогнать проект через IDE-рефакторинги: file-scoped namespaces, collection expressions, primary constructors.
- Заменить прямые вызовы `DateTime.UtcNow` на `TimeProvider`.
- Заменить `Dictionary` для справочника, который не меняется после старта, на `FrozenDictionary`.

## Вопросы с ответами
> [!question]- Какие возможности C# последних версий вы используете?
> Пример ответа: primary constructors и collection expressions для краткости, required/init для DTO, raw string для SQL и JSON, list и property patterns, `TimeProvider` для тестируемого времени, `FrozenDictionary` для справочников.

> [!question]- Что такое `TimeProvider` и зачем он?
> Абстракция над временем (`GetUtcNow`, таймеры) для внедрения через DI. В тестах подменяется `FakeTimeProvider`, время можно «перематывать».

> [!question]- Что дают collection expressions?
> Единый синтаксис `[..]` для массивов, списков, span и других коллекций, включая spread `..`; компилятор выбирает эффективную реализацию.

> [!question]- Чем LTS отличается от STS?
> LTS (чётные версии 8, 10) поддерживается 3 года, STS (нечётные, например 9) — 18 месяцев. Для продакшена чаще выбирают LTS.

> [!question]- Что такое HybridCache?
> Кэш .NET 9, объединяющий L1 (память процесса) и L2 (распределённый, например Redis) с защитой от массового одновременного пересчёта одного ключа (stampede).

## Связанные темы
- Предыдущая: [[N:3ea331048679818ea358eaece94428c4]] · Следующий раздел: [[N:3ea33104867981ba9b5adb98634471bf]]
- Платформа .NET: [[N:3ea3310486798179857cd5196aee4d71]]
- Records и primary constructors: [[N:3ea331048679810e866fff73c25c9cd8]]
- Pattern matching: [[N:3ea331048679818988ebed24b809cb9a]]
- Кэширование: [[N:3ea331048679815f8e29e329ae212176]]
