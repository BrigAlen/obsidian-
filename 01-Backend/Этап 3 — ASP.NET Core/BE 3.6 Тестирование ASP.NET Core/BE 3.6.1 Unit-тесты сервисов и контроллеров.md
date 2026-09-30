---
type: topic
domain: backend
stage: 3
section: "3.6"
order: 1
status: todo
level: middle
notion_id: 3ea331048679811e8935f94e6640714d
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/testing, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Unit-тесты сервисов и контроллеров

↑ [[BE 3.6 Тестирование ASP.NET Core|3.6 Тестирование ASP.NET Core]] · → [[BE 3.6.2 Интеграционные тесты — WebApplicationFactory|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Что тестировать на уровне unit, а что оставить интеграционным тестам.

## Объяснение

Тонкие контроллеры/endpoint-ы почти не содержат логики, поэтому unit-тестируют **сервисы и handlers**, а HTTP-слой — интеграционными тестами.

```csharp
public class OrderServiceTests
{
    private readonly InMemoryOrders _repo = new();
    private readonly FakeTimeProvider _time = new();

    [Fact]
    public async Task Cancel_paid_order_throws()
    {
        var order = await _repo.AddAsync(Order.Paid());
        var sut = new OrderService(_repo, _time);

        await Assert.ThrowsAsync<ConflictException>(() => sut.CancelAsync(order.Id, default));
    }
}
```

Контроллер тоже можно вызвать напрямую, если он возвращает `ActionResult<T>`:

```csharp
var result = await controller.Get(id, default);
var ok = Assert.IsType<OkObjectResult>(result.Result);
```

Но Minimal API-лямбды так не проверить — выносите обработчики в методы.

## Нюансы и подводные камни

- Unit-тесты не проверяют маршрутизацию, привязку, фильтры, сериализацию — для этого интеграционные тесты.
- Мок `DbContext` не показывает ошибок SQL — используйте реальную БД.
- Тестируйте поведение (что вернулось, что сохранилось), а не вызовы.
- Одна ответственность на тест, читаемые имена: `Method_State_Expected`.

## Практика

1. Покройте сервис заказов: позитивные и негативные сценарии.
2. Вынесите лямбды Minimal API в статические методы и протестируйте.
3. Проверьте отмену через `CancellationToken`.

## Вопросы с ответами

> [!question]- Что тестировать unit-ами в web API?
> Бизнес-логику сервисов и handlers, мапперы, валидаторы; HTTP-слой — интеграционными.

> [!question]- Стоит ли мокать DbContext?
> Нет: используйте настоящую БД (Testcontainers) или fake-репозиторий на границе.

## Связанные темы

- [[N:3ea3310486798124a799c04cc2451379]]
- [[N:3ea33104867981f78191c12d951a2073]]
