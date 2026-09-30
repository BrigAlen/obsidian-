---
type: topic
domain: backend
stage: 1
section: "1.3"
order: 8
status: todo
level: junior
notion_id: 3ea331048679812f9ce5e774db1a3627
tags: [domain/backend, stage/1, level/junior, topic/types, topic/records, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Enum, record, tuple, деконструкция

↑ [[BE 1.3 C♯ — основы языка|1.3 C♯: основы языка]] · ← [[BE 1.3.7 Исключения — try, catch, finally, when, свои исключения|Предыдущая]] · → [[BE 1.3.9 Pattern matching и switch expressions|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->


























































> [!info] Зачем это на собесе
> Эти четыре конструкции постоянно встречаются в современном C#-коде: enum для наборов значений, record для DTO и value object, tuple для возврата нескольких значений, деконструкция для разбора. Спросят про `[Flags]`, отличие record от class, `with`-выражение и про то, когда кортеж плохая идея.

> [!note] Переписано
> В Notion эта страница содержала шаблонный текст без отношения к теме. Здесь — содержательная версия.

## Объяснение

### Enum
Именованный набор целочисленных констант (по умолчанию `int`, значения с 0).
```csharp
public enum AppointmentStatus { Booked = 1, Arrived = 2, Cancelled = 3 }

var s = AppointmentStatus.Booked;
Enum.TryParse<AppointmentStatus>("Arrived", ignoreCase: true, out var parsed);
Enum.IsDefined(typeof(AppointmentStatus), 99);   // false
```
- Базовый тип можно задать: `enum Level : byte { ... }`.
- `[Flags]` — набор битовых флагов, значения степени двойки; комбинируются `|`, проверяются `HasFlag` или `&`.
```csharp
[Flags]
public enum Permissions { None = 0, Read = 1, Write = 2, Delete = 4, All = Read | Write | Delete }

var p = Permissions.Read | Permissions.Write;
bool canWrite = p.HasFlag(Permissions.Write);   // true
```
- Приведение `(AppointmentStatus)42` компилируется и не бросает исключение, даже если такого значения нет — проверяйте `Enum.IsDefined` на входе из внешнего мира.
- В API числовые значения enum — часть контракта: не меняйте и не переупорядочивайте существующие значения. В JSON удобнее строки (`JsonStringEnumConverter`).

### Record
Ссылочный тип (`record` / `record class`) или значимый (`record struct`) с **равенством по значению** и удобными возможностями «из коробки».
```csharp
public sealed record PatientDto(Guid Id, string LastName, DateOnly BirthDate);

var a = new PatientDto(id, "Иванов", new DateOnly(1990, 5, 1));
var b = a with { LastName = "Петров" };     // неразрушающая копия
Console.WriteLine(a == new PatientDto(id, "Иванов", new DateOnly(1990, 5, 1)));  // true, сравнение по значению
Console.WriteLine(a);                       // PatientDto { Id = ..., LastName = Иванов, ... }
```
Что генерирует компилятор: конструктор, свойства (для позиционных — `init`), `Equals`/`GetHashCode`, `==`/`!=`, `ToString`, `Deconstruct`, метод `Clone` для `with`.
- Позиционный синтаксис `record R(int A, string B)` даёт неизменяемые свойства; обычный синтаксис `record R { public int A { get; init; } }` — тоже.
- Наследование возможно только между record: `record Student(...) : Person(...)`.
- `record struct` (C# 10): значимый тип; `readonly record struct` — иммутабельный (рекомендуется для value object).
- Подходит: DTO, сообщения, value object, ключи словарей, результаты. Не подходит: сущности EF Core с изменяемым состоянием (там равенство по Id, а не по значениям).

### Tuple
```csharp
(int Count, decimal Sum) Aggregate(IEnumerable<Item> items) =>
    (items.Count(), items.Sum(i => i.Price));

var (count, sum) = Aggregate(items);          // деконструкция
var t = Aggregate(items);
Console.WriteLine($"{t.Count}: {t.Sum}");     // именованные элементы
```
- `ValueTuple` — структура, элементы именованные только на этапе компиляции. Дёшево и без аллокаций.
- `System.Tuple` — старый ссылочный тип, элементы `Item1`, `Item2`; в новом коде не нужен.
- Сравнение кортежей по значению: `(1, "a") == (1, "a")`.

### Деконструкция
```csharp
var (id, name) = patient;                     // требует метод Deconstruct или позиционный record
public void Deconstruct(out Guid id, out string name) { id = Id; name = Name; }

var (x, _) = point;                           // discard — ненужный элемент
foreach (var (key, value) in dictionary) { }  // KeyValuePair деконструируется
(a, b) = (b, a);                              // обмен значений без временной переменной
```

## Нюансы и подводные камни
- Enum без значения `0`: `default(MyEnum)` равен 0 и будет «неопределённым» значением. Добавляйте `None`/`Unknown = 0` или начинайте с осмысленного значения.
- `[Flags]` без степеней двойки даст неожиданные комбинации.
- `Enum.ToString()` и `Enum.Parse` используют рефлексию и медленнее ручного `switch`; на горячем пути — `switch` или генерация.
- record с изменяемыми свойствами (`{ get; set; }`) ломает предположение об иммутабельности: `with` копирует, но оригинал можно изменить.
- Равенство record для полей-коллекций — по ссылке, а не по содержимому: `List<int>` в record сравнивается как ссылка.
- Кортежи хороши для локальных возвратов; в публичном API лучше именованный тип: у кортежа нет собственного смысла, его нельзя расширить и сложнее версионировать.
- `with` работает только с record и struct (с C# 10), у обычного класса его нет.

## Примеры для практики
- Сделать `readonly record struct Money(decimal Amount, string Currency)` с оператором сложения, запретить сложение разных валют.
- Enum `[Flags]` прав доступа с методами `Grant` и `Revoke`.
- Метод, возвращающий `(bool Success, string? Error)`, и его замена на Result-тип.

## Вопросы с ответами
> [!question]- Чем record отличается от class?
> Компилятор генерирует равенство по значению, `ToString`, `Deconstruct` и `with`-копирование. По умолчанию record ссылочный, иммутабельный по духу и предназначен для данных.

> [!question]- Что делает `with`?
> Создаёт копию record (или struct), меняя указанные свойства. Оригинал не изменяется.

> [!question]- Для чего `[Flags]` у enum и как проверять флаг?
> Позволяет хранить комбинацию значений в одной переменной (значения — степени двойки). Проверка через `HasFlag` или побитово `(value & flag) == flag`.

> [!question]- Чем ValueTuple отличается от Tuple?
> ValueTuple — значимый тип, изменяемые поля, имена элементов существуют только на этапе компиляции. Tuple — ссылочный неизменяемый класс с `Item1..ItemN`. В новом коде используется ValueTuple.

> [!question]- Что произойдёт при приведении `(MyEnum)99`, если такого значения нет?
> Исключения не будет: в переменной окажется число 99. Валидность проверяют через `Enum.IsDefined` или `switch` с ветвью по умолчанию.

> [!question]- Когда нельзя полагаться на равенство record по значению?
> Когда поля содержат коллекции или другие ссылочные типы без собственного равенства: они сравниваются по ссылке.

## Связанные темы
- Предыдущая: [[N:3ea3310486798167aae3ed222aeb634e]] · Следующая: [[N:3ea331048679818988ebed24b809cb9a]]
- Value и reference типы: [[N:3ea33104867981948314ef0273ece7b5]]
- Pattern matching и positional-паттерны: [[N:3ea331048679818988ebed24b809cb9a]]
- Equals и GetHashCode: [[N:3ea33104867981339ec6f0b777d85f83]]
