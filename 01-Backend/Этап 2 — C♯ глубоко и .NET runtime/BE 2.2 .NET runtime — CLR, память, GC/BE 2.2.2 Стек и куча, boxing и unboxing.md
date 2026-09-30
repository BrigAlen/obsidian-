---
type: topic
domain: backend
stage: 2
section: "2.2"
order: 2
status: todo
level: middle
notion_id: 3ea3310486798189a6e7d196b6eac221
tags: [domain/backend, stage/2, level/middle, topic/memory, topic/boxing, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Стек и куча, boxing и unboxing

↑ [[BE 2.2 .NET runtime — CLR, память, GC|2.2 .NET runtime: CLR, память, GC]] · ← [[BE 2.2.1 CLR, IL, JIT, AOT, tiered compilation|Предыдущая]] · → [[BE 2.2.3 Сборщик мусора — поколения, LOH, режимы GC|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> boxing — скрытый источник аллокаций и нагрузки на GC. Вопросы «что такое boxing, где он происходит неявно» и «где хранится value type внутри класса» задают почти всегда.

## Объяснение

### Стек и управляемая куча (повтор с углублением)

- **Стек потока**: кадры методов, локальные value types, ссылки. Освобождается при выходе из метода.
- **Управляемая куча (managed heap)**: объекты ссылочных типов. Каждый объект имеет **заголовок** (sync block index, 8 байт на x64) и **указатель на таблицу методов** (MethodTable, 8 байт) — минимум 24 байта на объект.
- Value type **внутри** объекта (поле класса, элемент массива) хранится в куче в составе этого объекта.
- Локальная переменная, **захваченная замыканием** или живущая через `await`, переносится в объект в куче (display class или state machine).

### Boxing и unboxing

**Boxing** — упаковка value type в объект в куче, когда его используют как `object` или интерфейс.
**Unboxing** — извлечение значения обратно с проверкой типа.
```csharp
int x = 42;
object o = x;            // boxing: аллокация объекта в куче + копирование значения
int y = (int)o;          // unboxing: проверка типа + копирование
long z = (long)o;        // InvalidCastException! распаковывать можно только в точный тип
```

### Где boxing происходит неявно

```csharp
// 1. Необобщённые коллекции (legacy)
var list = new ArrayList(); list.Add(1);                   // boxing

// 2. Приведение struct к интерфейсу
IComparable c = 5;                                         // boxing
void Print(IFormattable f) {} Print(DateTime.Now);        // boxing

// 3. params object[] и форматирование (до .NET 6)
string.Format("{0} {1}", id, count);                       // boxing int-ов
Console.WriteLine("{0}", 42);
_logger.LogInformation("Count {Count}", count);           // boxing в params object?[] → LoggerMessage решает

// 4. Вызов методов object у struct без переопределения
myStruct.GetHashCode();  myStruct.Equals(other);           // ValueType.Equals — рефлексия и boxing
myStruct.ToString();                                        // если не переопределён

// 5. Enum в некоторых API
someEnum.HasFlag(Flags.A);                                  // до .NET Core 2.1 — boxing, теперь интринсик
Enum.GetName(...)

// 6. dynamic, рефлексия Invoke, сравнение generic без ограничений через ==(object)
```

### Как избегать

- Generic-коллекции и методы (`List<int>`, `where T : IComparable<T>`) — без боксинга.
- Переопределять `Equals`, `GetHashCode`, `ToString` у struct или использовать `record struct`, реализовать `IEquatable<T>`.
- Интерполяция строк (.NET 6+) без боксинга (handlers). `[LoggerMessage]` для логов.
- Не приводить struct к интерфейсу в горячем коде, использовать generic-ограничения.

### Как увидеть

- IL-инструкция `box` в декомпиляторе (sharplab.io).
- BenchmarkDotNet `[MemoryDiagnoser]` — неожиданные аллокации.
- Анализаторы (Roslynator, HeapAllocationAnalyzer, ErrorProne.NET).

## Нюансы и подводные камни

- Изменение упакованной struct через интерфейс меняет **копию в куче**, а не исходную переменную.
- Boxing сам по себе — наносекунды, но в цикле на миллион элементов это миллион мусорных объектов и лишние сборки GC.
- `Dictionary<MyStruct, T>` без `IEquatable<MyStruct>` боксит ключ при каждом сравнении.
- Nullable: `object o = (int?)null` → `o == null` (null не боксится). `(int?)5` боксится как `int`, а не как `Nullable<int>`.

## Тестирование

```csharp
[MemoryDiagnoser]
public class BoxingBench
{
    private readonly int[] _data = Enumerable.Range(0, 1000).ToArray();
    [Benchmark] public int WithBoxing() { var l = new ArrayList(); foreach (var x in _data) l.Add(x); return l.Count; }
    [Benchmark] public int Generic()    { var l = new List<int>();  foreach (var x in _data) l.Add(x); return l.Count; }
}
// в отчёте колонка Allocated покажет разницу
```

## Вопросы с ответами

> [!question]- Что такое boxing и unboxing?
> Boxing — упаковка value type в объект в куче при приведении к object или интерфейсу (аллокация и копирование). Unboxing — извлечение значения обратно с проверкой точного типа.

> [!question]- Где boxing происходит неявно?
> Необобщённые коллекции, приведение struct к интерфейсу, params object[] (Format, старое логирование), вызов непереопределённых Equals, GetHashCode и ToString у struct, dynamic и рефлексия.

> [!question]- Где хранится int-поле объекта класса?
> В куче, внутри памяти самого объекта. На стеке хранятся только локальные переменные и параметры (если они не захвачены замыканием или async).

> [!question]- Сколько памяти занимает пустой объект в .NET на x64?
> Минимум 24 байта: заголовок объекта (8), указатель на MethodTable (8) и минимальное поле или выравнивание (8).

> [!question]- Можно ли распаковать упакованный int в long?
> Нет, будет InvalidCastException. Распаковывать нужно в точный тип, затем преобразовывать: (long)(int)o.

## Связанные темы

- Предыдущая: [[N:3ea331048679811dbdcde35749fbe9b4]] · Следующая: [[N:3ea33104867981ff9626d62f5afa884d]]
- Value и reference типы: [[N:3ea33104867981948314ef0273ece7b5]]
- Память процесса: [[N:3ea33104867981129550de5de3011878]]
- Equals и GetHashCode: [[N:3ea33104867981339ec6f0b777d85f83]]
- Аллокации и zero-alloc: [[N:3ea33104867981fb8c07fdd4f935833b]]
