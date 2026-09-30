---
type: topic
domain: backend
stage: 5
section: "5.7"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981fa9871f6da12aaf8b4
tags: [domain/backend, stage/5, level/middle, topic/testing, topic/integration, topic/http, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Моки внешних HTTP-сервисов: WireMock.Net, HttpMessageHandler

↑ [[BE 5.7 Тестирование интеграций|5.7 Тестирование интеграций]] · → [[BE 5.7.2 Контрактные тесты — Pact, проверка proto и GraphQL-схем|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Как тестировать код, вызывающий внешние API, без реальных вызовов и нестабильности.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Способ | Что это | Когда |
|---|---|---|
| Подмена `HttpMessageHandler` | fake-обработчик, возвращающий заготовленный ответ | unit-тесты клиента, без сети |
| WireMock.Net | настоящий HTTP-сервер-заглушка со сценариями | интеграционные тесты, проверка сериализации, заголовков, таймаутов |
| Контрактный тест (Pact) | проверка соглашения между потребителем и поставщиком | защита от расхождения контрактов |
| Sandbox провайдера | тестовая среда внешней системы | ручные/e2e проверки |

```csharp
// WireMock.Net
using var server = WireMockServer.Start();
server.Given(Request.Create().WithPath("/v2/charges").UsingPost().WithHeader("Idempotency-Key", "*"))
      .RespondWith(Response.Create().WithStatusCode(201).WithBodyAsJson(new { id = "ch_1", status = "succeeded" }));

var gateway = new AcmePaymentGateway(new HttpClient { BaseAddress = new Uri(server.Url!) });
var result = await gateway.ChargeAsync(charge, default);
Assert.Equal(PaymentStatus.Succeeded, result.Status);
```

Сценарии сбоев (главная ценность моков):

```csharp
server.Given(Request.Create().WithPath("/v2/charges").UsingPost())
      .InScenario("retry").WillSetStateTo("second").RespondWith(Response.Create().WithStatusCode(503));
server.Given(Request.Create().WithPath("/v2/charges").UsingPost())
      .InScenario("retry").WhenStateIs("second").RespondWith(Response.Create().WithStatusCode(201).WithBodyAsJson(ok));
// задержка: Response.Create().WithDelay(TimeSpan.FromSeconds(5)) — проверить таймаут
```

Fake handler:

```csharp
class StubHandler(HttpResponseMessage response) : HttpMessageHandler
{
    public HttpRequestMessage? Last;
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage r, CancellationToken ct) { Last = r; return Task.FromResult(response); }
}
```

## Нюансы и подводные камни

- Мок отражает ваши предположения: при изменении настоящего API тест остаётся зелёным. Дополняйте контрактными тестами и проверкой на sandbox.
- Проверяйте не только успех: 4xx/5xx, таймауты, некорректный JSON, лишние поля.
- Не мокайте `HttpClient` через `Mock<HttpClient>`: подменяйте handler.
- В `WebApplicationFactory` внешний адрес подставляйте через конфигурацию на URL WireMock.
- Порты WireMock выбирайте динамически для параллельных тестов.

## Практика

1. Напишите тесты клиента платёжного API на WireMock: успех, 503→успех, таймаут, 400.
2. Проверьте, что клиент отправляет `Idempotency-Key` и корректный JSON.
3. Запишите ответы реального API как заготовки (record/playback).

## Вопросы с ответами

> [!question]- Чем WireMock лучше подмены HttpMessageHandler?
> Проходит настоящий HTTP-стек (сериализация, заголовки, таймауты, ретраи) и позволяет описывать сценарии сбоев.

> [!question]- Какой недостаток у моков внешних API?
> Они могут разойтись с реальностью; нужны контрактные тесты и периодическая проверка на sandbox.

## Связанные темы

- [[N:3ea33104867981f3b6f9f4a53a5b5df9]]
- [[N:3ea33104867981028d7fdb121c3dcd02]]
