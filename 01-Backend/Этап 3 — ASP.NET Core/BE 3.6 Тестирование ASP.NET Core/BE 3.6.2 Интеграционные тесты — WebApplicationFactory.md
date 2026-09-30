---
type: topic
domain: backend
stage: 3
section: "3.6"
order: 2
status: todo
level: middle
notion_id: 3ea3310486798124a799c04cc2451379
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/testing, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Интеграционные тесты: WebApplicationFactory

↑ [[BE 3.6 Тестирование ASP.NET Core|3.6 Тестирование ASP.NET Core]] · ← [[BE 3.6.1 Unit-тесты сервисов и контроллеров|Предыдущая]] · → [[BE 3.6.3 Testcontainers — настоящие БД и брокеры в тестах|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->











> [!info] Зачем это на собесе
> Самый ценный вид тестов для API: весь конвейер в памяти без реального сервера.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`WebApplicationFactory<Program>` запускает приложение в памяти (`TestServer`) и даёт `HttpClient`.

```csharp
public class ApiFactory : WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Testing");
        builder.ConfigureTestServices(s =>
        {
            s.RemoveAll<IPaymentGateway>();
            s.AddSingleton<IPaymentGateway, FakePaymentGateway>();   // заменяем внешнее
        });
    }
}

public class OrdersTests(ApiFactory f) : IClassFixture<ApiFactory>
{
    [Fact]
    public async Task Create_returns_201_and_location()
    {
        var client = f.CreateClient();
        var resp = await client.PostAsJsonAsync("/orders", new { customer = "A", quantity = 1 });

        Assert.Equal(HttpStatusCode.Created, resp.StatusCode);
        Assert.NotNull(resp.Headers.Location);
    }
}
```

Для этого в `Program.cs` нужен `public partial class Program { }` (при top-level statements).

## Нюансы и подводные камни

- Заменяйте только внешние границы (платежи, почта); внутренности оставляйте настоящими.
- Изолируйте данные между тестами: отдельная схема/БД или очистка (Respawn).
- Аутентификацию подменяют тестовым handler-ом (см. [[N:3ea3310486798199a2e6f67582af01e4]]).
- Фоновые сервисы в тестах отключайте или подменяйте.
- Общий `IClassFixture` — общий сервер: не хранить в нём изменяемое состояние.

## Практика

1. Напишите тесты на CRUD заказов через `WebApplicationFactory`.
2. Подключите Respawn для очистки БД между тестами.
3. Подмените внешний HTTP-сервис с помощью WireMock.Net.

## Вопросы с ответами

> [!question]- Что даёт WebApplicationFactory?
> Полноценный запуск приложения в памяти с реальным конвейером, DI и конфигурацией без сетевого порта.

> [!question]- Как подменить зависимость в тесте?
> `ConfigureTestServices` или `WithWebHostBuilder`.

> [!question]- Как изолировать данные тестов?
> Отдельная БД на класс, транзакции с откатом либо Respawn.

## Связанные темы

- [[N:3ea331048679811e8935f94e6640714d]]
- [[N:3ea331048679810e9b74c450d13d065b]]
