---
type: topic
domain: backend
stage: 1
section: "1.3"
order: 5
status: todo
level: junior
notion_id: 3ea331048679815fb1d0cd967cf4bffe
tags: [domain/backend, stage/1, level/junior, topic/nullability, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Nullable: значимые типы и nullable reference types

↑ [[BE 1.3 C♯ — основы языка|1.3 C♯: основы языка]] · ← [[BE 1.3.4 Строки — иммутабельность, StringBuilder, интерполяция, сравнение|Предыдущая]] · → [[BE 1.3.6 Методы и параметры — ref, out, in, params, именованные аргументы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->







































> [!info] Зачем это на собесе
> `NullReferenceException` — самая частая ошибка в .NET. Nullable reference types (NRT) переносят её обнаружение на этап компиляции. Спросят разницу `int?` и `string?` и операторы `?.`, `??`, `!`.

## Объяснение

### Nullable value types — Nullable\<T\>

Value type не может быть null. `int?` = `Nullable<int>` — структура с полями `HasValue` и `Value`.
```csharp
int? age = null;
if (age.HasValue) Console.WriteLine(age.Value);
int years = age ?? 0;                // значение по умолчанию
int? next = age + 1;                 // «поднятые» операторы: null + 1 = null
age.GetValueOrDefault();             // 0
```
В EF Core `int?` отображается на nullable-колонку, `int` — на `NOT NULL`.

### Nullable reference types (C# 8+)

Включаются в проекте: `<Nullable>enable</Nullable>`. После этого:
- `string` — «не может быть null», компилятор предупреждает при присвоении null.
- `string?` — «может быть null», компилятор требует проверки перед разыменованием.
Это **только статический анализ**: в рантайме `string` и `string?` — один тип, проверок нет.
```csharp
public class Patient
{
    public required string LastName { get; init; }   // обязателен при создании
    public string? MiddleName { get; init; }         // может отсутствовать
}

string GetDisplayName(Patient p)
{
    // p.MiddleName.Length;                          // warning CS8602: возможное разыменование null
    return p.MiddleName is null ? p.LastName : $"{p.LastName} {p.MiddleName}";
}
```

### Операторы

```csharp
var city = patient?.Address?.City;          // null-conditional: null, если по пути null
var len = patient?.Name?.Length ?? 0;       // null-coalescing
options.Timeout ??= TimeSpan.FromSeconds(30); // присвоить, если null
handler?.Invoke(this, args);                // вызвать делегат, если есть
string name = maybeName!;                   // null-forgiving: «я уверена, что не null» — отключает предупреждение
```

### Атрибуты для анализатора

```csharp
bool TryGetPatient(Guid id, [NotNullWhen(true)] out Patient? patient) { ... }
if (TryGetPatient(id, out var p)) Console.WriteLine(p.LastName);   // здесь p не null, без предупреждения

[return: NotNullIfNotNull(nameof(input))] string? Normalize(string? input) => input?.Trim();
static void ThrowIfNull([NotNull] object? value) { ... }
ArgumentNullException.ThrowIfNull(dto);            // guard-метод
ArgumentException.ThrowIfNullOrWhiteSpace(code);
```

### Паттерны проверки

```csharp
if (patient is null) return NotFound();       // предпочтительно: не вызывает перегруженный ==
if (patient is not null) { ... }
if (patient is { Address.City: var city }) Console.WriteLine(city);  // property pattern
```

## Нюансы и подводные камни

- `!` (null-forgiving) — «заглушить» компилятор. Частое `!` = проблема в дизайне. Допустимо в тестах и в местах, где инициализацию гарантирует фреймворк (например, `DbSet<T>` в DbContext: `= null!`).
- Десериализация JSON может положить null в не-nullable свойство: NRT этого не видит. Валидируйте DTO (`required`, FluentValidation).
- EF Core учитывает NRT: не-nullable `string` → колонка `NOT NULL`. Включение NRT в старом проекте может сгенерировать миграцию, меняющую nullability колонок.
- Для generic-кода: `T?` для неограниченного T означает «default(T)», а не Nullable.
- `default` для struct — «нулевые» поля, а не null. Проверка `if (dateTime == null)` для `DateTime` всегда false.

## Тестирование

```csharp
[Fact]
public void Display_name_without_middle_name()
{
    var p = new Patient { LastName = "Иванова", MiddleName = null };
    GetDisplayName(p).Should().Be("Иванова");
}
```

## Вопросы с ответами

> [!question]- Чем int? отличается от string?
> int? — это реальный тип Nullable\<int\>, структура с HasValue и Value. string? — аннотация для статического анализа при включённых NRT: в рантайме это тот же string.

> [!question]- Что дают nullable reference types?
> Компилятор отслеживает, где может быть null, и предупреждает о возможных NullReferenceException до запуска. Контракты «может быть null» становятся явными в сигнатурах.

> [!question]- Что делает оператор ! после выражения?
> Null-forgiving operator: говорит компилятору считать значение не-null и убирает предупреждение. На рантайм не влияет.

> [!question]- Почему is null лучше, чем == null?
> Оператор == может быть перегружен в типе, а is null всегда проверяет именно ссылку. К тому же это единый стиль с pattern matching.

> [!question]- Гарантирует ли не-nullable свойство, что там не будет null после десериализации?
> Нет. NRT — только анализ компилятора. JSON-сериализатор может записать null. Нужны required-свойства, настройки сериализатора и валидация.

## Связанные темы

- Предыдущая: [[N:3ea33104867981278c7bd1c2c8906499]] · Следующая: [[N:3ea33104867981fab5abd8e186ca973d]]
- Records и required: [[N:3ea331048679810e866fff73c25c9cd8]]
- Валидация DTO: [[N:3ea33104867981f59cb0d625e950c6cb]]
- Моделирование в EF Core: [[N:3ea33104867981bfbfc4ec436ba6c342]]
- Optional chaining в JS: [[N:3ea33104867981faa9bafdc336eee7fb]]
