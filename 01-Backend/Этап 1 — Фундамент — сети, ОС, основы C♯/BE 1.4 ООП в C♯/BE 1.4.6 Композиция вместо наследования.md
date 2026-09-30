---
type: topic
domain: backend
stage: 1
section: "1.4"
order: 6
status: todo
level: junior
notion_id: 3ea33104867981ccaa52e78aa5b0c0da
tags: [domain/backend, stage/1, level/junior, topic/oop, topic/composition, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Композиция вместо наследования

↑ [[BE 1.4 ООП в C♯|1.4 ООП в C♯]] · ← [[BE 1.4.5 Полиморфизм и инкапсуляция на практике|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->























































> [!info] Зачем это на собесе
> «Почему композиция лучше наследования?» — вопрос на понимание дизайна. На senior-уровне ждут умения показать, как переделать хрупкую иерархию в набор взаимозаменяемых компонентов.

## Объяснение

- **Наследование** — отношение «является» (is-a). Сильная связь: наследник зависит от деталей реализации базового класса, иерархия фиксируется при компиляции.
- **Композиция** — отношение «имеет» или «использует» (has-a). Объект собирается из других объектов через интерфейсы, поведение можно менять и комбинировать, в том числе в рантайме.

### Проблема наследования: комбинаторный взрыв

```csharp
// Нужны отчёты: PDF или Excel × с подписью или без × с водяным знаком или без
class Report {}
class PdfReport : Report {}
class SignedPdfReport : PdfReport {}
class WatermarkedSignedPdfReport : SignedPdfReport {}
class SignedExcelReport : ExcelReport {}   // … 8 классов, и каждый новый признак удваивает число
```

### Решение композицией

```csharp
public interface IReportExporter { byte[] Export(Document doc); }        // PDF, Excel
public interface IDocumentDecorator { void Apply(Document doc); }       // подпись, водяной знак, QR

public sealed class ReportGenerator(
    IDataCollector collector,
    IReportExporter exporter,
    IEnumerable<IDocumentDecorator> decorators)
{
    public async Task<byte[]> GenerateAsync(ReportRequest req, CancellationToken ct)
    {
        var data = await collector.CollectAsync(req, ct);
        var doc = Layout(data);
        foreach (var d in decorators) d.Apply(doc);    // любое сочетание без новых классов
        return exporter.Export(doc);
    }
}
```
Новый формат экспорта — новый `IReportExporter`. Новое оформление — новый `IDocumentDecorator`. Существующий код не меняется.

### Паттерны, построенные на композиции

- **Strategy** — подменяемый алгоритм через интерфейс (экспорт в разные форматы).
- **Decorator** — обёртка, добавляющая поведение (кэширующий репозиторий поверх обычного, логирующий HttpMessageHandler).
- **Adapter** — приведение чужого API к своему интерфейсу (клиент 1С → `IAccountingGateway`).
```csharp
// Decorator: кэш поверх сервиса терминологии, без изменения исходного класса
public sealed class CachedTerminologyService(ITerminologyService inner, IMemoryCache cache) : ITerminologyService
{
    public Task<Concept?> LookupAsync(string system, string code, CancellationToken ct) =>
        cache.GetOrCreateAsync($"{system}|{code}", _ => inner.LookupAsync(system, code, ct));
    public Task<IReadOnlyList<Concept>> ExpandAsync(string url, CancellationToken ct) => inner.ExpandAsync(url, ct);
}
// регистрация с Scrutor: services.Decorate<ITerminologyService, CachedTerminologyService>();
```

### Когда наследование уместно

- Настоящая иерархия «является» со стабильным базовым типом (исключения, базовые классы фреймворка: `ControllerBase`, `BackgroundService`, `DbContext`).
- Template Method с общим алгоритмом и небольшими вариациями.
- Неглубоко: 1–2 уровня.

## Нюансы и подводные камни

- Композиция добавляет интерфейсов и классов. Для простого случая без вариативности это оверинжиниринг.
- Слишком много мелких абстракций усложняет навигацию по коду: «куда делась логика?».
- Декораторы в DI удобно регистрировать через Scrutor или вручную фабрикой. Порядок декораторов важен (кэш снаружи логирования или наоборот).
- Во фронтенде тот же принцип: composables вместо mixins, слоты вместо наследования компонентов.

## Тестирование

Композиция упрощает тесты: каждую часть тестируют отдельно, остальные подменяют.
```csharp
[Fact]
public async Task Cache_calls_inner_once()
{
    var inner = Substitute.For<ITerminologyService>();
    inner.LookupAsync("s", "c", Arg.Any<CancellationToken>()).Returns(new Concept("c"));
    var sut = new CachedTerminologyService(inner, new MemoryCache(new MemoryCacheOptions()));
    await sut.LookupAsync("s", "c", default);
    await sut.LookupAsync("s", "c", default);
    await inner.Received(1).LookupAsync("s", "c", Arg.Any<CancellationToken>());
}
```

## Вопросы с ответами

> [!question]- Почему композицию предпочитают наследованию?
> Слабее связанность (зависимость от интерфейсов, а не от реализации базового класса), гибкое комбинирование поведения без взрыва числа классов, замена в рантайме и в тестах, нет проблемы хрупкого базового класса.

> [!question]- Когда наследование всё-таки оправдано?
> Когда есть настоящее отношение «является» со стабильной базой, при расширении базовых классов фреймворка и для Template Method с неглубокой иерархией.

> [!question]- Приведите пример Decorator из .NET или вашего проекта.
> DelegatingHandler в HttpClient (логирование, ретраи, заголовки), Stream-обёртки (GZipStream над FileStream), кэширующий сервис поверх сервиса терминологии.

> [!question]- Как переделать иерархию отчётов с комбинаторным взрывом?
> Выделить оси изменения в интерфейсы (формат экспорта, оформление, источник данных) и собирать генератор из реализаций через DI вместо наследования под каждое сочетание.

## Связанные темы

- Предыдущая: [[N:3ea331048679813f8c82f603f6921990]] · Следующий раздел (коллекции и LINQ): [[N:3ea33104867981aea93acb54f1006c79]]
- Структурные паттерны (Decorator, Adapter): [[N:3ea33104867981d99fb3d9af9f9dec4f]]
- Поведенческие (Strategy): [[N:3ea33104867981f88d7cefc97436250e]]
- Keyed services и декораторы в DI: [[N:3ea331048679816788e0df486d1eca06]]
- Composables во Vue (та же идея): [[N:3ea33104867981c78367f30abc89391d]]
