---
type: topic
domain: backend
stage: 2
section: "2.4"
order: 2
status: todo
level: middle
notion_id: 3ea331048679817289b6e475ce642e50
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/testing, topic/xunit, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# xUnit: Fact, Theory, fixtures, параллелизм

↑ [[BE 2.4 Тестирование в .NET — основы|2.4 Тестирование в .NET — основы]] · ← [[BE 2.4.1 Виды тестов и пирамида в .NET|Предыдущая]] · → [[BE 2.4.3 Тестовые двойники — Moq и NSubstitute|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





















































> [!info] Зачем это на собесе
> Спрашивают, как устроены жизненный цикл теста и общие фикстуры, и почему тесты в одном классе не идут параллельно.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

xUnit — основной фреймворк для тестов на .NET. Для каждого тестового метода создаётся **новый экземпляр класса**, поэтому конструктор играет роль setup, а `IDisposable.Dispose` — teardown.

| Атрибут | Назначение |
|---|---|
| `[Fact]` | обычный тест без параметров |
| `[Theory]` + `[InlineData]` | параметризованный тест |
| `[MemberData]`, `[ClassData]` | данные из свойства или класса |
| `IClassFixture<T>` | общий контекст на все тесты класса |
| `ICollectionFixture<T>` + `[Collection]` | общий контекст на несколько классов |
| `IAsyncLifetime` | асинхронные setup/teardown |
| `[Trait("cat","slow")]` | категории для фильтрации |

```csharp
public class PriceTests
{
    [Theory]
    [InlineData(100, 0.1, 90)]
    [InlineData(200, 0.25, 150)]
    public void Applies_discount(decimal price, decimal rate, decimal expected)
        => Assert.Equal(expected, Pricing.Discount(price, rate));
}
```

### Фикстуры

```csharp
public class DbFixture : IAsyncLifetime
{
    public string ConnectionString { get; private set; } = "";
    public async Task InitializeAsync() { /* поднять контейнер */ }
    public async Task DisposeAsync() { /* остановить */ }
}

public class RepoTests : IClassFixture<DbFixture>
{
    private readonly DbFixture _db;
    public RepoTests(DbFixture db) => _db = db;
}
```

### Параллелизм

Тестовые классы (коллекции) выполняются параллельно, тесты внутри класса — последовательно. Общее состояние между классами нужно изолировать либо объединить классы в одну `[Collection]`.

## Нюансы и подводные камни

- Статическое состояние делает тесты зависимыми и ломается при параллельном запуске.
- `async void` в тестах недопустим: используйте `async Task`.
- Не полагайтесь на порядок выполнения тестов.
- Выводите диагностику через `ITestOutputHelper`, а не `Console`.
- Для тестов на исключения: `await Assert.ThrowsAsync<T>(() => ...)`.

## Практика

1. Превратите три похожих `[Fact]` в один `[Theory]`.
2. Сделайте `IClassFixture` с общей БД и очисткой данных между тестами.
3. Отключите параллелизм для одной коллекции и проверьте, что состояние не «протекает».

## Вопросы с ответами

> [!question]- Сколько раз создаётся экземпляр тестового класса?
> На каждый тест создаётся новый экземпляр. Общие ресурсы выносят в фикстуры.

> [!question]- Чем IClassFixture отличается от ICollectionFixture?
> Первая — общий объект на один класс, вторая — на все классы, входящие в коллекцию.

> [!question]- Как xUnit распараллеливает тесты?
> По тестовым коллекциям: разные классы могут идти одновременно, тесты одного класса — по очереди.

> [!question]- Чем xUnit отличается от NUnit и MSTest?
> Новый экземпляр на тест, нет `[SetUp]/[TearDown]` (конструктор и Dispose), фикстуры через интерфейсы; NUnit использует один экземпляр по умолчанию и атрибуты setup.

## Связанные темы

- [[N:3ea33104867981f78191c12d951a2073]]
- [[N:3ea33104867981b18627d30f782b4713]]
