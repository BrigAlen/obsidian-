---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 8
status: todo
level: middle
notion_id: 3ea33104867981548d57ffd75d21ec61
tags: [domain/backend, stage/2, level/middle, topic/span, topic/memory, topic/performance, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Span и Memory: stackalloc, ref struct

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.7 Records, init, with, required, primary constructors|Предыдущая]] · → [[BE 2.1.9 Атрибуты и рефлексия|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> `Span<T>` — главный инструмент высокопроизводительного .NET: парсинг, работа с буферами и файлами без аллокаций. На senior-собесе спросят, что такое Span, чем он отличается от Memory и почему Span нельзя использовать в async.

## Объяснение

### Span\<T\> и ReadOnlySpan\<T\>

**Непрерывный участок памяти** любого происхождения: массив, часть массива, строка, память на стеке (`stackalloc`), нативная память. Это `ref struct`: указатель + длина, **без копирования** данных.
```csharp
int[] arr = [1, 2, 3, 4, 5];
Span<int> middle = arr.AsSpan(1, 3);    // [2, 3, 4] — вид на тот же массив, без копии
middle[0] = 20;                          // arr[1] теперь 20

ReadOnlySpan<char> s = "Иванова Анна Петровна".AsSpan();
var space = s.IndexOf(' ');
ReadOnlySpan<char> lastName = s[..space];      // подстрока без аллокации (в отличие от Substring)

Span<byte> buffer = stackalloc byte[256];      // буфер на стеке — ноль аллокаций в куче
```

### Парсинг без аллокаций

```csharp
// разбор строки "J06.9;J20.0;I10" без Split (Split создаёт массив и строки)
static int CountCodes(ReadOnlySpan<char> input)
{
    var count = 0;
    foreach (var range in input.Split(';'))       // .NET 9: MemoryExtensions.Split по Span
        if (!input[range].Trim().IsEmpty) count++;
    return count;
}

int.Parse("12345".AsSpan(1, 3));               // парсинг части строки
Utf8Formatter.TryFormat(value, buffer, out var written);
```

### Ограничения ref struct

Span живёт **только на стеке**:
- нельзя хранить в поле класса, в обычной struct, в массиве;
- нельзя боксить, приводить к `object` или интерфейсу;
- нельзя использовать через `await` (в async-методах — с C# 13 можно в синхронных участках между await) и в итераторах `yield`;
- нельзя захватить лямбдой.
Причина: Span может указывать на стек текущего метода, и хранение его дольше жизни метода дало бы висячую ссылку.

### Memory\<T\> и ReadOnlyMemory\<T\>

Обычная struct (не ref struct) — «Span, который можно хранить»: поле класса, передача через `await`. Когда нужно работать — `memory.Span`.
```csharp
public async Task ProcessAsync(ReadOnlyMemory<byte> data, CancellationToken ct)
{
    await _stream.WriteAsync(data, ct);          // Stream API принимает Memory
    Parse(data.Span);                            // синхронная обработка — через Span
}
```

### Где это есть в .NET

`Stream.ReadAsync(Memory<byte>)`, `System.Text.Json` (Utf8JsonReader — ref struct на Span), `PipeReader`/`PipeWriter` (System.IO.Pipelines — Kestrel), `ArrayPool<T>` + Span, `string.Create`, `SearchValues<T>` (.NET 8) для быстрого поиска символов, `CollectionsMarshal.AsSpan(list)`.

### Связка с ArrayPool

```csharp
var rented = ArrayPool<byte>.Shared.Rent(64 * 1024);          // взять буфер из пула (может быть больше запрошенного)
try
{
    int read;
    while ((read = await source.ReadAsync(rented.AsMemory(), ct)) > 0)
        await target.WriteAsync(rented.AsMemory(0, read), ct);
}
finally { ArrayPool<byte>.Shared.Return(rented); }            // обязательно вернуть
```

## Нюансы и подводные камни

- `stackalloc` большого размера → `StackOverflowException`. Правило: до ~1 КБ на стеке, больше — `ArrayPool`.
- Span поверх арендованного массива нельзя использовать после `Return` — это use-after-free на уровне логики.
- Не оптимизируйте преждевременно: Span нужен в горячих путях (парсеры, сериализация, обработка потоков), а не в каждом контроллере.
- `ToString()`/`ToArray()` у Span возвращает копию — аллокация.

## Тестирование

Производительность проверяют бенчмарком, корректность — обычными тестами:
```csharp
[Theory]
[InlineData("A;B; ;C", 3)]
[InlineData("", 0)]
public void Counts_codes(string input, int expected) => CountCodes(input).Should().Be(expected);
```
```csharp
[MemoryDiagnoser]
public class ParseBench
{
    [Benchmark(Baseline = true)] public int SplitCount() => "A;B;C".Split(';').Length;
    [Benchmark] public int SpanCount() => CountCodes("A;B;C");   // сравнить Allocated
}
```

## Вопросы с ответами

> [!question]- Что такое Span?
> ref struct, представляющая непрерывный участок памяти (массив, строка, стек, нативная память) без копирования. Позволяет резать, парсить и обрабатывать данные без аллокаций.

> [!question]- Почему Span нельзя хранить в поле класса и использовать через await?
> Span может указывать на стек метода. Объект в куче или async state machine переживают метод, и ссылка стала бы висячей. Поэтому это ref struct, живущий только на стеке.

> [!question]- Чем Memory отличается от Span?
> Memory — обычная структура, которую можно хранить в полях и передавать через await. Span — только на стеке, но быстрее. Memory превращается в Span через свойство .Span для синхронной обработки.

> [!question]- Как обработать большой файл без выделения больших массивов?
> Потоковое чтение Stream с буфером из ArrayPool (или System.IO.Pipelines), обработка через Span и Memory, возврат буфера в пул.

## Связанные темы

- Предыдущая: [[N:3ea331048679810e866fff73c25c9cd8]] · Следующая: [[N:3ea331048679819dabaffeca732fabc4]]
- Стек и куча: [[N:3ea3310486798189a6e7d196b6eac221]]
- Пулы объектов: [[N:3ea3310486798178b6c3ebe2c2759604]]
- Аллокации и zero-alloc код: [[N:3ea33104867981fb8c07fdd4f935833b]]
- BenchmarkDotNet: [[N:3ea33104867981419025f0bdbcb02acf]]
