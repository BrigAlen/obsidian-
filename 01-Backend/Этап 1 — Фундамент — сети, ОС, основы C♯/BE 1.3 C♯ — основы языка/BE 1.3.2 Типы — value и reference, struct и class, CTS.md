---
type: topic
domain: backend
stage: 1
section: "1.3"
order: 2
status: todo
level: junior
notion_id: 3ea33104867981948314ef0273ece7b5
tags: [domain/backend, stage/1, level/junior, topic/types, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Типы: value и reference, struct и class, CTS

↑ [[BE 1.3 C♯ — основы языка|1.3 C♯: основы языка]] · ← [[BE 1.3.1 Платформа .NET — SDK, runtime, версии, сборки, NuGet, solution и csproj|Предыдущая]] · → [[BE 1.3.3 Переменные, var, const и readonly, преобразования типов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

















































> [!info] Зачем это на собесе
> вопрос №1 на C#-собесе: «чем value type отличается от reference type, struct от class». Отсюда растут boxing, копирование, `Equals`, производительность и баги с изменением копии.

## Объяснение

### Common Type System (CTS)

Все типы .NET наследуются от `System.Object`. Две категории:
- **Value types** (`struct`, `enum`, встроенные числовые, `bool`, `char`, `DateTime`, `Guid`, `decimal`, `Nullable<T>`, кортежи `ValueTuple`) — наследуются от `System.ValueType`.
- **Reference types** (`class`, `interface`, `delegate`, `record` (class), массивы, `string`, `object`).

### Семантика копирования — главное отличие

```csharp
struct PointS { public int X; }
class  PointC { public int X; }

var s1 = new PointS { X = 1 };
var s2 = s1;        // копия ВСЕХ данных
s2.X = 99;
Console.WriteLine(s1.X);  // 1

var c1 = new PointC { X = 1 };
var c2 = c1;        // копия ССЫЛКИ, объект один
c2.X = 99;
Console.WriteLine(c1.X);  // 99
```
- Переменная value type **содержит данные**, reference type — **ссылку** на объект в куче.
- Передача в метод по умолчанию — **по значению**: для struct копируются данные, для class — ссылка (метод может изменить объект, но не заменить ссылку вызывающего без `ref`).

### Сравнение struct и class

- **Память:** struct — inline (на стеке или внутри содержащего объекта), class — всегда куча + заголовок объекта (16 байт на x64) + ссылка.
- **null:** struct не может быть null (только `Nullable<T>`), class может.
- **Наследование:** struct нельзя наследовать (неявно sealed), но можно реализовывать интерфейсы.
- **Значение по умолчанию:** struct — все поля нулевые (`default`), class — `null`.
- **Равенство:** struct по умолчанию сравнивается по значениям полей (через рефлексию, медленно — переопределяйте `Equals` или используйте `record struct`), class — по ссылке.
- **Конструктор без параметров:** у struct всегда есть (с C# 10 можно объявить свой).

### Когда выбирать struct

Рекомендации Microsoft: небольшой (≲16 байт), логически одно значение (координата, деньги, диапазон дат), **иммутабельный**, редко боксится. Примеры в BCL: `DateTime`, `TimeSpan`, `Guid`, `KeyValuePair`.
```csharp
public readonly record struct Money(decimal Amount, string Currency);   // иммутабельный, с равенством по значению
```

### string — особый reference type

Ссылочный тип, но **иммутабельный** и сравнивается `==` по содержимому (перегружен оператор). Поэтому ведёт себя «как значение».

### Специальные виды struct

- `readonly struct` — все поля readonly, компилятор избегает защитных копий.
- `ref struct` (`Span<T>`) — живёт только на стеке: нельзя боксить, хранить в полях класса, использовать в async (до C# 13 с ограничениями).

## Нюансы и подводные камни

- **Мутабельная struct — источник багов:**
```csharp
var list = new List<PointS> { new() { X = 1 } };
// list[0].X = 5;           // ошибка компиляции: индексатор возвращает КОПИЮ
var p = list[0]; p.X = 5;   // меняется копия, в списке по-прежнему 1
```
- Большие struct дорого копировать: передавайте через `in` или делайте class.
- struct как ключ Dictionary без переопределённых `Equals`/`GetHashCode` — медленно (рефлексия и boxing). Используйте `record struct` или реализуйте `IEquatable<T>`.
- Приведение struct к интерфейсу боксит её, и изменения через интерфейс идут в копию.
- Большой массив struct — один объект в куче (хорошо для кэша CPU). Массив class — массив ссылок + N объектов.

## Тестирование

```csharp
[Fact]
public void Struct_is_copied_on_assignment()
{
    var a = new Money(10, "BYN");
    var b = a with { Amount = 20 };
    a.Amount.Should().Be(10);
    (a == new Money(10, "BYN")).Should().BeTrue();   // record struct: равенство по значению
}
```

## Вопросы с ответами

> [!question]- Чем value type отличается от reference type?
> Переменная value type содержит сами данные, при присваивании и передаче они копируются. Reference type хранит ссылку на объект в куче: копируется ссылка, объект общий. Value types не бывают null (кроме Nullable), не наследуются.

> [!question]- Когда использовать struct вместо class?
> Для небольших иммутабельных значений, которые логически представляют одно значение (деньги, координаты, интервал) и создаются в больших количествах. Это снижает нагрузку на GC.

> [!question]- string — value или reference type? Почему ведёт себя как значение?
> Reference type, но иммутабельный, и оператор == сравнивает содержимое. Любое «изменение» создаёт новую строку.

> [!question]- Почему мутабельные struct считаются плохой практикой?
> Из-за неявных копий (индексаторы, свойства, боксинг, readonly-поля) изменения часто применяются к копии и теряются. Это трудноуловимые баги.

> [!question]- Можно ли наследовать struct? Реализовать интерфейс?
> Наследовать нельзя: struct неявно sealed и наследуется от ValueType. Реализовать интерфейсы можно, но приведение к интерфейсу вызывает boxing.

## Связанные темы

- Предыдущая: [[N:3ea3310486798179857cd5196aee4d71]] · Следующая: [[N:3ea331048679812d8d6ccc547b012764]]
- Стек, куча и boxing: [[N:3ea3310486798189a6e7d196b6eac221]]
- Память процесса: [[N:3ea33104867981129550de5de3011878]]
- Equals и GetHashCode: [[N:3ea33104867981339ec6f0b777d85f83]]
- Records: [[N:3ea331048679810e866fff73c25c9cd8]]
- Типы в JS (для сравнения): [[N:3ea3310486798101bb32e955dc77616f]]
