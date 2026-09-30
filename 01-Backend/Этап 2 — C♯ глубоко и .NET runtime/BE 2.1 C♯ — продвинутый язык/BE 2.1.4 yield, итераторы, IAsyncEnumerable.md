---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798160917dfb8938b23233
tags: [domain/backend, stage/2, level/middle, topic/iterators, topic/async, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# yield, итераторы, IAsyncEnumerable

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.3 LINQ глубоко — отложенное выполнение, IEnumerable и IQueryable, expression trees|Предыдущая]] · → [[BE 2.1.5 Generics глубоко — constraints, вариантность, static abstract|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
































































> [!info] Зачем это на собесе
> `yield` объясняет, как работает LINQ и отложенное выполнение. `IAsyncEnumerable` позволяет стримить большие выборки из БД и ClickHouse, читать постраничные внешние API и отдавать данные клиенту без загрузки всего в память.

## Объяснение

### yield return

Метод с `yield return` компилируется в **класс-итератор** (конечный автомат, state machine). Тело выполняется по частям при каждом `MoveNext()`.
```csharp
public static IEnumerable<int> Range(int from, int count)
{
    for (var i = 0; i < count; i++)
    {
        Console.WriteLine($"generate {from + i}");
        yield return from + i;            // приостановка: значение отдано, состояние сохранено
    }
    // yield break; — досрочное завершение
}

foreach (var n in Range(1, 3).Take(2)) Console.WriteLine(n);
// generate 1, 1, generate 2, 2 — третий элемент даже не сгенерирован
```
- Код до первого `yield` **не выполняется** до первого `MoveNext()`. Отсюда нюанс с валидацией аргументов: исключение появится не при вызове метода, а при переборе.
```csharp
public static IEnumerable<T> Batch<T>(IEnumerable<T> source, int size)
{
    ArgumentOutOfRangeException.ThrowIfNegativeOrZero(size);   // НЕ сработает при вызове Batch(...)!
    return Iterator();                                          // решение: валидировать снаружи, итератор — локальная функция
    IEnumerable<T> Iterator() { var buf = new List<T>(size); foreach (var x in source) { buf.Add(x); if (buf.Count == size) { yield return buf; buf = new(size); } } if (buf.Count > 0) yield return buf; }
}
```
- `try/finally` в итераторе выполнится при `Dispose()` перечислителя (`foreach` вызывает его автоматически, в том числе при `break`).

### IAsyncEnumerable\<T\> и await foreach

Асинхронный поток: каждый элемент может ожидать I/O.
```csharp
// чтение постраничного внешнего API (FHIR Bundle, 1С OData, Битрикс24 — все отдают страницами)
public async IAsyncEnumerable<Patient> ReadAllAsync([EnumeratorCancellation] CancellationToken ct = default)
{
    string? next = "/Patient?_count=100";
    while (next is not null)
    {
        var page = await _http.GetFromJsonAsync<Page<Patient>>(next, ct);
        foreach (var p in page!.Items) yield return p;
        next = page.NextLink;
    }
}

await foreach (var patient in client.ReadAllAsync(ct))
    await mapper.UpsertAsync(patient, ct);            // обработка по мере поступления
```
- `[EnumeratorCancellation]` связывает токен из `WithCancellation(ct)` с параметром.
- В связке с EF Core: `db.Observations.AsAsyncEnumerable()` читает строки из курсора потоково.
- ASP.NET Core умеет возвращать `IAsyncEnumerable<T>` из эндпоинта — JSON-массив стримится клиенту.
```csharp
app.MapGet("/api/export/observations", (AppDb db, CancellationToken ct) =>
    db.Observations.AsNoTracking().Where(o => o.Date >= from).AsAsyncEnumerable());
```

### System.Linq.Async и .NET 10

Операторы LINQ для `IAsyncEnumerable` (`WhereAwait`, `SelectAwait`, `ToListAsync`) — пакет `System.Linq.Async`. В .NET 10 они вошли в BCL (`System.Linq.AsyncEnumerable`).

### Channels как альтернатива

Когда производитель и потребитель работают независимо (разная скорость, несколько потребителей) — `Channel<T>` и его `ReadAllAsync()` (тоже `IAsyncEnumerable`).

## Нюансы и подводные камни

- Итератор, возвращённый из метода с `using` (например, DbContext или соединение), выполнится **после** выхода из метода, когда ресурс уже освобождён. Ресурс должен жить внутри итератора.
- Повторное перечисление итератора выполняет генерацию заново (повторные запросы к API или БД).
- `yield` нельзя использовать в `try` с `catch` (только `try/finally`), в лямбдах и с `ref`/`out`-параметрами.
- Стриминг из EF Core держит соединение и курсор открытыми всё время перебора: не делайте долгую обработку каждого элемента, иначе блокируете соединение из пула.

## Тестирование

```csharp
[Fact]
public async Task Reads_all_pages()
{
    var handler = new FakePagedHandler(pages: 3, perPage: 2);   // HttpMessageHandler-заглушка
    var client = new FhirClient(new HttpClient(handler) { BaseAddress = new("http://test") });
    var items = await client.ReadAllAsync().ToListAsync();
    items.Should().HaveCount(6);
}
```

## Вопросы с ответами

> [!question]- Как работает yield return?
> Компилятор превращает метод в класс-итератор со state machine. Каждый MoveNext выполняет код до следующего yield return, сохраняя состояние локальных переменных. Выполнение ленивое.

> [!question]- Почему валидация аргументов в методе с yield «не срабатывает»?
> Тело итератора, включая проверки, выполняется только при первом MoveNext, а не при вызове метода. Проверки выносят в обычный метод, который возвращает внутренний итератор.

> [!question]- Зачем IAsyncEnumerable, если есть Task\<List\<T>>?
> Чтобы обрабатывать и отдавать элементы по мере поступления: меньше памяти и задержка до первого результата, поддержка отмены на любом шаге, стриминг больших данных.

> [!question]- Что такое EnumeratorCancellation?
> Атрибут для параметра CancellationToken в асинхронном итераторе. Связывает его с токеном, переданным через WithCancellation при await foreach.

## Связанные темы

- Предыдущая: [[N:3ea33104867981dc98c9f760e86a24d5]] · Следующая: [[N:3ea33104867981d085d7ec58153f8c7b]]
- Итераторы и генераторы в JS: [[N:3ea33104867981e6b8fdfbbecd2a548e]]
- Channels: [[N:3ea331048679817e96d8c67b432324e0]]
- Загрузка и стриминг файлов: [[N:3ea331048679813385bfc8013c2dc64f]]
- Интеграции со сторонними API: [[N:3ea33104867981e6845fee5306c0eb22]]
