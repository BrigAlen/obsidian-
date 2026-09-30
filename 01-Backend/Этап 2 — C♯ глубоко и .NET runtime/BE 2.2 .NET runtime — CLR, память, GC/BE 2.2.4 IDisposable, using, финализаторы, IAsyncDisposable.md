---
type: topic
domain: backend
stage: 2
section: "2.2"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981dcbbedd3d78a7442c0
tags: [domain/backend, stage/2, level/middle, topic/dispose, topic/memory, priority/must]
reviewed:
next_review:
priority: must
time: 8
---

# IDisposable, using, финализаторы, IAsyncDisposable

↑ [[BE 2.2 .NET runtime — CLR, память, GC|2.2 .NET runtime: CLR, память, GC]] · ← [[BE 2.2.3 Сборщик мусора — поколения, LOH, режимы GC|Предыдущая]] · → [[BE 2.2.5 Утечки памяти в .NET и как их искать|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









































> [!info] Зачем это на собесе
> GC освобождает только управляемую память, а соединения с БД, файлы, сокеты и HTTP-ответы надо закрывать явно. Спросят паттерн Dispose, разницу `Dispose` и финализатора, `using` и кто освобождает сервисы в DI.

## Объяснение

### Управляемые и неуправляемые ресурсы

- **Управляемая память** — освобождает GC.
- **Неуправляемые ресурсы** — дескрипторы ОС (файлы, сокеты), соединения с БД, нативная память, блокировки. GC о них не знает и не может своевременно освободить.

### IDisposable и using

```csharp
using (var conn = new NpgsqlConnection(cs)) { ... }          // Dispose в finally

using var file = File.OpenRead(path);                          // using-объявление: Dispose в конце области видимости
await using var conn = await dataSource.OpenConnectionAsync(ct);   // IAsyncDisposable — асинхронное освобождение
```
`using` — это `try { ... } finally { obj?.Dispose(); }`. Ресурс освобождается даже при исключении.

### IAsyncDisposable

Для ресурсов, чьё закрытие требует I/O (сброс буфера в сеть, закрытие соединения): `DisposeAsync()`. Пример: `DbConnection`, `Stream`, `DbContext`, клиенты брокеров.

### Реализация Dispose (упрощённый современный вариант)

Если класс **только владеет другими IDisposable** (частый случай) — финализатор не нужен:
```csharp
public sealed class ReportRenderer : IDisposable, IAsyncDisposable
{
    private readonly MemoryStream _buffer = new();
    private readonly Report _report = new();                   // FastReport — IDisposable
    private bool _disposed;

    public void Dispose()
    {
        if (_disposed) return;
        _report.Dispose();
        _buffer.Dispose();
        _disposed = true;
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed) return;
        _report.Dispose();
        await _buffer.DisposeAsync();
        _disposed = true;
    }

    public byte[] Render() { ObjectDisposedException.ThrowIf(_disposed, this); ... }
}
```

### Полный паттерн Dispose (для неsealed-классов с неуправляемым ресурсом)

```csharp
public class NativeHandleOwner : IDisposable
{
    private IntPtr _handle;          // неуправляемый ресурс (лучше обернуть в SafeHandle!)
    private bool _disposed;

    public void Dispose() { Dispose(true); GC.SuppressFinalize(this); }   // финализатор больше не нужен

    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;
        if (disposing) { /* освободить управляемые IDisposable-поля */ }
        if (_handle != IntPtr.Zero) { NativeFree(_handle); _handle = IntPtr.Zero; }   // неуправляемое — всегда
        _disposed = true;
    }

    ~NativeHandleOwner() => Dispose(false);   // финализатор — страховка, если Dispose забыли
}
```
На практике для нативных дескрипторов используют **`SafeHandle`** — он сам содержит финализатор, и свой финализатор писать не нужно.

### Финализатор (~Class)

- Вызывается GC **недетерминированно** (когда-нибудь после того, как объект стал недостижим), в отдельном потоке финализации.
- Объект с финализатором переживает лишнюю сборку (попадает в очередь финализации) → дороже для GC.
- Нельзя обращаться к другим управляемым объектам (они могут быть уже собраны).
- Это **страховка**, а не способ освобождения ресурсов.

### Кто освобождает объекты в DI

- Сервисы, **созданные контейнером** и реализующие `IDisposable`/`IAsyncDisposable`, контейнер освобождает сам при завершении их scope (Scoped — в конце запроса, Singleton — при остановке приложения).
- Объекты, созданные вами через `new` внутри сервиса, освобождаете вы.
- Экземпляр, переданный при регистрации (`services.AddSingleton(new Foo())`), контейнер **не** освобождает.
- Не вызывайте `Dispose` у сервисов, полученных из DI, — ими владеет контейнер.

### Особые случаи

- `HttpClient`: не оборачивать в `using` на каждый запрос (исчерпание сокетов) → `IHttpClientFactory`.
- `DbContext`: в DI Scoped, освобождается автоматически. Вручную — через `IDbContextFactory` + `await using`.
- `HttpResponseMessage`, `Stream` из ответа — освобождать, иначе соединение не возвращается в пул.
- `CancellationTokenSource` с таймером (`CancelAfter`) — `Dispose`, чтобы остановить таймер.

## Нюансы и подводные камни

- Забытый `Dispose` у соединения с БД → исчерпание пула соединений (`The connection pool has been exhausted`).
- `Dispose` должен быть **идемпотентным** (безопасный повторный вызов) и не бросать исключений.
- Возврат `IDisposable` из метода передаёт владение вызывающему — документируйте это.
- `using` на объекте, который отдаётся наружу (например, возвращаемый Stream), закроет его до того, как вызывающий начнёт читать.

## Тестирование

```csharp
[Fact]
public void Throws_after_dispose()
{
    var r = new ReportRenderer();
    r.Dispose();
    r.Invoking(x => x.Render()).Should().Throw<ObjectDisposedException>();
}
```

## Вопросы с ответами

> [!question]- Зачем нужен IDisposable, если есть GC?
> GC управляет только памятью и делает это недетерминированно. Соединения, файлы, сокеты и другие неуправляемые ресурсы надо освобождать своевременно и явно — через Dispose.

> [!question]- Чем Dispose отличается от финализатора?
> Dispose вызывается явно и детерминированно (обычно через using). Финализатор вызывает GC когда-нибудь в отдельном потоке — это страховка, которая удорожает сборку мусора.

> [!question]- Зачем GC.SuppressFinalize в Dispose?
> Ресурсы уже освобождены, поэтому финализатор не нужен. Вызов убирает объект из очереди финализации, и он собирается быстрее и дешевле.

> [!question]- Кто освобождает сервисы, зарегистрированные в DI?
> Контейнер, для экземпляров, которые он сам создал: Scoped в конце scope (запроса), Singleton при остановке приложения, Transient — вместе со scope, в котором созданы.

> [!question]- Что такое IAsyncDisposable и когда нужен?
> Интерфейс с DisposeAsync для ресурсов, которые при закрытии выполняют асинхронный I/O (сброс буферов, закрытие соединений). Используется через await using.

## Связанные темы

- Предыдущая: [[N:3ea33104867981ff9626d62f5afa884d]] · Следующая: [[N:3ea331048679814cbeece465f98c6820]]
- Время жизни в DI: [[N:3ea331048679815b938fd2f3f2a7c66d]]
- HttpClient и IHttpClientFactory: [[N:3ea331048679813982d5cc11f4554a52]]
- DbContext: жизненный цикл: [[N:3ea33104867981c7a0d3ffbde71096db]]
- Файловые дескрипторы: [[N:3ea3310486798130af0ae91c7852a262]]
