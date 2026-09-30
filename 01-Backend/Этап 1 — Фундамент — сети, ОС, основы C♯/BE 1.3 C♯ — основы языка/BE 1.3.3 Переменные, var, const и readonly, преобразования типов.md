---
type: topic
domain: backend
stage: 1
section: "1.3"
order: 3
status: todo
level: junior
notion_id: 3ea331048679812d8d6ccc547b012764
tags: [domain/backend, stage/1, level/junior, topic/types, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Переменные, var, const и readonly, преобразования типов

↑ [[BE 1.3 C♯ — основы языка|1.3 C♯: основы языка]] · ← [[BE 1.3.2 Типы — value и reference, struct и class, CTS|Предыдущая]] · → [[BE 1.3.4 Строки — иммутабельность, StringBuilder, интерполяция, сравнение|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->
































> [!info] Зачем это на собесе
> `const` vs `readonly`, неявные и явные преобразования, `checked`, `decimal` для денег — частые вопросы. Ошибки здесь дают баги с округлением и переполнением.

## Объяснение

### var

Тип выводится компилятором из правой части **на этапе компиляции** — это по-прежнему строгая статическая типизация (не `dynamic`).
```csharp
var patients = new List<Patient>();   // тип List<Patient>
var total = 0m;                        // decimal
// var x;                             // ошибка: нужен инициализатор
```
Используйте, когда тип очевиден справа. Явный тип — когда он неочевиден (`var result = Calculate();`).

### const и readonly

- **`const`** — константа **времени компиляции**: только примитивы и строки, значение **вшивается** в IL в месте использования. Неявно static.
- **`readonly`** поле — присваивается в объявлении или в конструкторе, дальше не меняется. Значение вычисляется **в рантайме**, может быть любого типа.
- **`static readonly`** — одно значение на тип, вычисляется при инициализации типа.
```csharp
public class ReportSettings
{
    public const int MaxPages = 500;                              // вшивается в вызывающий код
    public static readonly TimeSpan Timeout = TimeSpan.FromSeconds(30); // в рантайме
    private readonly ILogger _log;                                 // только в конструкторе
    public ReportSettings(ILogger log) => _log = log;
}
```
> [!warning]
> Ловушка `const` между сборками: если библиотека поменяла `public const`, а зависимая сборка не пересобрана, в ней останется старое значение. Для публичных «констант», которые могут меняться, используйте `static readonly`.

`readonly` на поле ссылочного типа запрещает менять ссылку, но не содержимое объекта: `readonly List<int>` можно дополнять.

### Числовые типы

- Целые: `byte`, `short`, `int` (32 бита), `long` (64), беззнаковые `uint`, `ulong`.
- С плавающей точкой: `float`, `double` — двоичные, **неточные** для десятичных дробей (`0.1 + 0.2 != 0.3`).
- **`decimal`** — 128-битный десятичный, точный для денег и финансов, медленнее.
```csharp
0.1 + 0.2 == 0.3          // false (double)
0.1m + 0.2m == 0.3m       // true (decimal)
```

### Преобразования

- **Неявные** — без потери данных: `int → long`, `int → double`.
- **Явные (cast)** — с возможной потерей: `(int)3.9` → 3 (отбрасывание дробной части), `(int)longValue` — усечение.
- **Переполнение** по умолчанию молча «заворачивается» (`int.MaxValue + 1` = `int.MinValue`). `checked` бросает `OverflowException`.
```csharp
int big = int.MaxValue;
int wrapped = big + 1;               // -2147483648
int safe = checked(big + 1);         // OverflowException

int.Parse("42");                     // исключение при ошибке
if (int.TryParse(input, out var n)) { /* ... */ }  // без исключений — для пользовательского ввода
Convert.ToInt32(null);               // 0 (а int.Parse(null) — исключение)
decimal.Parse("1,5", new CultureInfo("ru-RU"));   // учитывайте культуру!
Math.Round(2.5);                     // 2 — банковское округление (к чётному) по умолчанию!
Math.Round(2.5, MidpointRounding.AwayFromZero);  // 3
```

### Операторы is, as и приведение ссылочных типов

```csharp
object o = GetEntity();
if (o is Patient p) Console.WriteLine(p.Name);   // pattern matching: проверка + приведение
var doc = o as DocumentReference;                 // null, если не тот тип (без исключения)
var enc = (Encounter)o;                           // InvalidCastException, если не тот тип
```

## Нюансы и подводные камни

- Деньги в `double` — баг. Только `decimal` (и `numeric` в PostgreSQL).
- `Math.Round` по умолчанию банковское: для отчётов с «школьным» округлением указывайте `MidpointRounding.AwayFromZero`.
- `Parse` без `CultureInfo` зависит от культуры сервера: в контейнере это InvariantCulture, у разработчика — ru-RU. Для машинных форматов — `CultureInfo.InvariantCulture`.
- `dynamic` отключает проверки компилятора: ошибки только в рантайме, медленнее. Нужен редко (COM, динамический JSON).
- Целочисленное деление: `5 / 2 == 2`. Нужно `5 / 2.0` или приведение.

## Тестирование

```csharp
[Theory]
[InlineData("1,5", 1.5)]
[InlineData("2", 2)]
public void Parses_russian_decimal(string input, decimal expected) =>
    decimal.Parse(input, new CultureInfo("ru-RU")).Should().Be(expected);
```

## Вопросы с ответами

> [!question]- Чем const отличается от readonly?
> const — значение времени компиляции (только примитивы и строки), вшивается в код вызывающих сборок, неявно static. readonly — присваивается при объявлении или в конструкторе, вычисляется в рантайме, может быть любого типа и быть экземплярным.

> [!question]- Почему для денег используют decimal?
> double и float двоичные и не могут точно представить многие десятичные дроби, отсюда ошибки округления. decimal хранит десятичную мантиссу и точен для финансовых расчётов.

> [!question]- Что будет при int.MaxValue + 1?
> По умолчанию переполнение без ошибки: int.MinValue. В контексте checked (или при включённой проверке в проекте) — OverflowException.

> [!question]- Чем is и as отличаются от явного приведения?
> Явное приведение бросает InvalidCastException при несовпадении типа. as возвращает null (только для ссылочных и nullable). is проверяет тип и в pattern matching сразу даёт типизированную переменную.

> [!question]- var — это динамическая типизация?
> Нет. Тип выводится при компиляции и фиксируется. Динамическая — это dynamic.

## Связанные темы

- Предыдущая: [[N:3ea33104867981948314ef0273ece7b5]] · Следующая: [[N:3ea33104867981278c7bd1c2c8906499]]
- Pattern matching: [[N:3ea331048679818988ebed24b809cb9a]]
- Кодировки и культура: [[N:3ea3310486798180a101f27fb02bd5ef]]
- Числа в JS: [[N:3ea3310486798101bb32e955dc77616f]]
