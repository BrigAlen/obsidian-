---
type: topic
domain: backend
stage: 2
section: "2.4"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981f78191c12d951a2073
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/testing, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Виды тестов и пирамида в .NET

↑ [[BE 2.4 Тестирование в .NET — основы|2.4 Тестирование в .NET — основы]] · → [[BE 2.4.2 xUnit — Fact, Theory, fixtures, параллелизм|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





























































> [!info] Зачем это на собесе
> «Какие бывают тесты и что вы тестируете в первую очередь?» — вопрос на зрелость. Ждут не перечисления, а логики выбора границы теста по риску.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Уровень | Что проверяет | Скорость | Хрупкость | Доля |
|---|---|---|---|---|
| Unit | одну единицу поведения без I/O | миллисекунды | низкая | большая |
| Integration | взаимодействие с реальной БД, очередью, HTTP-слоем | секунды | средняя | средняя |
| Contract | совместимость API между сервисами (Pact, OpenAPI) | быстро | низкая | по необходимости |
| End-to-end | пользовательский сценарий через всю систему | десятки секунд | высокая | малая |
| Нагрузочные, безопасность, mutation | нефункциональные свойства | долго | — | точечно |

Классическая пирамида: много быстрых unit-тестов внизу, меньше интеграционных, совсем мало E2E. Для сервисов на .NET часто работает «соты/бриллиант»: основная ценность в интеграционных тестах через `WebApplicationFactory` + Testcontainers, потому что бизнес-логика тонкая, а риски в SQL, сериализации и конфигурации.

### Что считать unit

Не «один класс», а «одна единица поведения». Тест, который знает о приватных вызовах и порядке обращений к мокам, ломается при рефакторинге и не защищает поведение.

### Структура теста: Arrange–Act–Assert

```csharp
[Fact]
public async Task Returns_not_found_for_missing_order()
{
    // Arrange
    var sut = new GetOrderHandler(new InMemoryOrders());

    // Act
    var result = await sut.Handle(new GetOrder(Guid.NewGuid()), CancellationToken.None);

    // Assert
    result.Should().BeOfType<NotFound>();
}
```

### Интеграционный тест API

```csharp
public class OrdersApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;
    public OrdersApiTests(WebApplicationFactory<Program> f) => _client = f.CreateClient();

    [Fact]
    public async Task Get_unknown_order_returns_404()
    {
        var resp = await _client.GetAsync($"/orders/{Guid.NewGuid()}");
        Assert.Equal(HttpStatusCode.NotFound, resp.StatusCode);
    }
}
```

## Нюансы и подводные камни

- Тесты деталей реализации (проверка вызовов приватных зависимостей) мешают рефакторингу.
- Coverage не равен качеству: строка выполнена, но ничего не проверено.
- Мок БД вместо настоящей скрывает ошибки SQL и миграций; для этого нужен Testcontainers.
- Тесты не должны зависеть друг от друга, порядка запуска и текущего времени.
- Flaky-тесты подрывают доверие к CI: чините или удаляйте, не перезапускайте по кругу.

## Практика

1. Возьмите свой сервис и разложите существующие тесты по уровням пирамиды.
2. Напишите один интеграционный тест на эндпоинт через `WebApplicationFactory`.
3. Сформулируйте, какие риски не покрыты, и выберите вид теста под каждый.

## Вопросы с ответами

> [!question]- Что такое пирамида тестирования?
> Модель распределения тестов: много быстрых изолированных unit-тестов, меньше интеграционных и минимум сквозных, так как высокие уровни дороже и хрупче.

> [!question]- Когда unit-тест бесполезен?
> Когда проверяет детали реализации или тривиальный код-проброс; тогда он повторяет код и ломается при рефакторинге без пользы.

> [!question]- Зачем нужны Testcontainers?
> Дают реальную БД/брокер в Docker на время теста, поэтому проверяется настоящий SQL, миграции и поведение драйвера.

> [!question]- Чем integration отличается от E2E?
> Integration проверяет часть системы с реальными зависимостями (API + БД), E2E — весь пользовательский путь, включая UI и внешние сервисы.

## Связанные темы

- [[N:3ea331048679817289b6e475ce642e50]]
- [[N:3ea33104867981a2ad5ff285f83ecce9]]
