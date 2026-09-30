---
type: topic
domain: backend
stage: 1
section: "1.3"
order: 9
status: todo
level: junior
notion_id: 3ea331048679818988ebed24b809cb9a
tags: [domain/backend, stage/1, level/junior, topic/patterns, priority/must]
reviewed:
next_review:
priority: must
time: 7
---

# Pattern matching и switch expressions

↑ [[BE 1.3 C♯ — основы языка|1.3 C♯: основы языка]] · ← [[BE 1.3.8 Enum, record, tuple, деконструкция|Предыдущая]] · → [[BE 1.3.10 Equals, GetHashCode, сравнение объектов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

































> [!info] Зачем это на собесе
> pattern matching делает код компактным и безопасным: маппинг статусов, обработка разных типов ресурсов, валидация. Современный C#-код ждут на собесе, а не цепочки if/else с приведениями.

## Объяснение

### Виды паттернов

```csharp
object value = GetValue();

// тип + переменная
if (value is Patient p) Console.WriteLine(p.LastName);

// константа и null
if (value is null) return;
if (status is AppointmentStatus.Cancelled) { ... }

// отрицание, и/или
if (value is not string) { ... }
if (age is >= 18 and < 65) { ... }            // relational + логический
if (code is "A" or "B" or "C") { ... }

// property pattern — проверка свойств (в т. ч. вложенных)
if (patient is { Address.City: "Минск", BirthDate.Year: < 2000 }) { ... }

// positional (для типов с Deconstruct, records)
if (point is (0, 0)) Console.WriteLine("origin");

// list patterns (C# 11)
if (args is [var first, .., var last]) { ... }
if (codes is ["ICD-10", _, ..]) { ... }
```

### switch expression

```csharp
string ToRu(AppointmentStatus s) => s switch
{
    AppointmentStatus.Booked    => "Записан",
    AppointmentStatus.Arrived   => "Пришёл",
    AppointmentStatus.Cancelled => "Отменён",
    _ => throw new ArgumentOutOfRangeException(nameof(s), s, null),
};

decimal Discount(Patient p) => p switch
{
    { Age: >= 65 }                    => 0.2m,
    { IsVeteran: true }               => 0.15m,
    { Age: < 18, HasInsurance: true } => 0.1m,
    null                              => throw new ArgumentNullException(nameof(p)),
    _                                 => 0m,
};

// обработка разных типов ресурсов (как в фабриках, мапперах)
string Describe(IResource r) => r switch
{
    Patient p            => $"Пациент {p.LastName}",
    Encounter { Status: "finished" } e => $"Визит {e.Id} завершён",
    Encounter e          => $"Визит {e.Id}",
    Observation o when o.Value > o.Threshold => "Отклонение от нормы",
    _                    => r.GetType().Name,
};
```

### switch statement с паттернами

```csharp
switch (ex)
{
    case PatientNotFoundException nf: return Results.NotFound(nf.Message);
    case ValidationException { Errors.Count: > 0 } ve: return Results.ValidationProblem(ve.ToDictionary());
    case OperationCanceledException: return Results.StatusCode(499);
    default: throw ex;
}
```
Компилятор проверяет **полноту** switch expression по enum и типам и предупреждает о недостижимых ветках (порядок важен: частное выше общего).

## Нюансы и подводные камни

- Switch expression без `_` бросает `SwitchExpressionException` на непредусмотренном значении. Лучше явно `_ => throw ...` с понятным сообщением.
- Большие switch по типам — возможный сигнал, что нужен полиморфизм (метод в каждом типе) или паттерн Strategy.
- `is` с property pattern безопасен к null: `x is { Name: "A" }` вернёт false для null.
- Паттерны не работают с произвольными выражениями справа: только константы, типы, relational-операторы.

## Тестирование

```csharp
[Theory]
[InlineData(70, false, 0.2)]
[InlineData(30, true, 0.15)]
[InlineData(30, false, 0)]
public void Discount_rules(int age, bool veteran, decimal expected) =>
    Discount(new Patient { Age = age, IsVeteran = veteran }).Should().Be(expected);
```

## Вопросы с ответами

> [!question]- Какие виды паттернов есть в C#?
> Type, constant (включая null), relational (\<, \>=), логические (and, or, not), property, positional (через Deconstruct), list patterns, var и discard (_).

> [!question]- Чем switch expression лучше switch statement?
> Это выражение: возвращает значение, компактнее, нет break, компилятор проверяет полноту и недостижимые ветки. Хорошо сочетается с паттернами.

> [!question]- Как безопасно проверить вложенное свойство на значение, если объект может быть null?
> Property pattern: `x is { Address.City: "Минск" }` — вернёт false, если x или Address равны null.

> [!question]- Когда pattern matching по типам — плохой дизайн?
> Когда большой switch по типам нужно дополнять при каждом новом типе и он дублируется в разных местах. Лучше полиморфизм или Strategy, где поведение лежит в самих типах.

## Связанные темы

- Предыдущая: [[N:3ea331048679812f9ce5e774db1a3627]] · Следующая: [[N:3ea33104867981339ec6f0b777d85f83]]
- Enum и record: [[N:3ea331048679812f9ce5e774db1a3627]]
- Полиморфизм: [[N:3ea331048679813f8c82f603f6921990]]
- Поведенческие паттерны (Strategy): [[N:3ea33104867981f88d7cefc97436250e]]
- Narrowing в TypeScript (аналог): [[N:3ea331048679812694a2d2a4ca78bc40]]
