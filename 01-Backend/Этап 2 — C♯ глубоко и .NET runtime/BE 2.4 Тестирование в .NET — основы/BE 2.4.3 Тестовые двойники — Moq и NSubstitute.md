---
type: topic
domain: backend
stage: 2
section: "2.4"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981b18627d30f782b4713
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/testing, topic/mocking, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Тестовые двойники: Moq и NSubstitute

↑ [[BE 2.4 Тестирование в .NET — основы|2.4 Тестирование в .NET — основы]] · ← [[BE 2.4.2 xUnit — Fact, Theory, fixtures, параллелизм|Предыдущая]] · → [[BE 2.4.4 FluentAssertions и AutoFixture|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


























> [!info] Зачем это на собесе
> Ждут, что вы отличаете mock, stub и fake и понимаете, где мок вредит. Частая ловушка — «мокать всё».

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Двойник | Что делает |
|---|---|
| Dummy | заглушка параметра, не используется |
| Stub | возвращает заранее заданные данные |
| Fake | упрощённая рабочая реализация (in-memory репозиторий) |
| Mock | проверяет, что взаимодействие произошло |
| Spy | записывает вызовы для последующей проверки |

Принцип: **stub для входящих зависимостей, mock только для исходящих побочных эффектов** (отправка письма, публикация события).

### NSubstitute

```csharp
var clock = Substitute.For<IClock>();
clock.UtcNow.Returns(new DateTime(2025, 1, 1));

var mailer = Substitute.For<IMailer>();
var sut = new OrderService(clock, mailer);

await sut.ConfirmAsync(order);

await mailer.Received(1).SendAsync(Arg.Is<Mail>(m => m.To == order.Email));
```

### Moq

```csharp
var repo = new Mock<IOrderRepository>();
repo.Setup(r => r.FindAsync(id, It.IsAny<CancellationToken>()))
    .ReturnsAsync(new Order(id));

var sut = new GetOrderHandler(repo.Object);
var result = await sut.Handle(new GetOrder(id), default);

repo.Verify(r => r.FindAsync(id, It.IsAny<CancellationToken>()), Times.Once);
```

### Fake вместо мока

```csharp
class InMemoryOrders : IOrderRepository
{
    private readonly Dictionary<Guid, Order> _db = new();
    public Task<Order?> FindAsync(Guid id, CancellationToken ct) => Task.FromResult(_db.GetValueOrDefault(id));
    public Task AddAsync(Order o, CancellationToken ct) { _db[o.Id] = o; return Task.CompletedTask; }
}
```

Fake устойчивее к рефакторингу, потому что проверяет результат, а не последовательность вызовов.

## Нюансы и подводные камни

- Не мокайте типы, которыми не владеете (`DbContext`, `HttpClient`): оборачивайте в свой интерфейс или используйте настоящие зависимости.
- Верификация каждого вызова делает тест копией реализации.
- Моки без `Strict` возвращают значения по умолчанию, ошибки настройки маскируются.
- Moq использует динамические прокси и не умеет мокать не-виртуальные члены и `static`.
- Для времени используйте `TimeProvider` и `FakeTimeProvider`.

## Практика

1. Замените мок репозитория на in-memory fake и сравните хрупкость тестов.
2. Проверьте отправку письма моком, а расчёт цены — без моков.
3. Напишите тест на повторную попытку с помощью stub, который сначала бросает исключение.

## Вопросы с ответами

> [!question]- Чем mock отличается от stub?
> Stub подаёт данные в тест, mock проверяет, что вызов произошёл. Проверять нужно результат; моки — для побочных эффектов на границах.

> [!question]- Когда мокать не стоит?
> Для собственной чистой логики, DbContext и типов сторонних библиотек: тест перестаёт отражать реальную работу.

> [!question]- Moq или NSubstitute?
> Функционально близки: у NSubstitute проще синтаксис, у Moq больше распространён. Важнее договориться о единстве стиля в команде.

## Связанные темы

- [[N:3ea331048679817289b6e475ce642e50]]
- [[N:3ea33104867981c6ad5ae1bb29d7bce3]]
