---
type: topic
domain: backend
stage: 5
section: "5.7"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981028d7fdb121c3dcd02
tags: [domain/backend, stage/5, level/middle, topic/testing, topic/contracts, topic/pact, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Контрактные тесты: Pact, проверка proto и GraphQL-схем

↑ [[BE 5.7 Тестирование интеграций|5.7 Тестирование интеграций]] · ← [[BE 5.7.1 Моки внешних HTTP-сервисов — WireMock.Net, HttpMessageHandler|Предыдущая]] · → [[BE 5.7.3 Тестирование gRPC-сервисов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Как командам микросервисов не ломать друг друга при изменениях API.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Контрактный тест** проверяет, что обе стороны интеграции согласны с форматом сообщений, не поднимая всю систему.

**Consumer-driven contracts (Pact)**:

1. Потребитель описывает ожидаемые запросы и ответы, тест на моке провайдера формирует файл-контракт (pact).
2. Контракт публикуется в Pact Broker.
3. Поставщик в CI проигрывает контракты против реальной реализации.
4. `can-i-deploy` блокирует релиз, ломающий контракт потребителей.

```csharp
var pact = Pact.V4("orders-ui", "orders-api", new PactConfig());
var http = pact.WithHttpInteractions();
http.UponReceiving("get order").Given("order 42 exists")
    .WithRequest(HttpMethod.Get, "/orders/42")
    .WillRespond().WithStatus(200).WithJsonBody(new { id = 42, status = Match.Type("paid") });

await http.VerifyAsync(async ctx => { var o = await new OrdersClient(ctx.MockServerUri).GetAsync(42); Assert.Equal("paid", o.Status); });
```

Для схем без Pact:

| Технология | Проверка |
|---|---|
| OpenAPI | линтер (Spectral), сравнение схем (`oasdiff breaking`) |
| gRPC/proto | `buf breaking` против основной ветки |
| GraphQL | `graphql-inspector diff`, проверка на реальных запросах клиентов |
| События (Kafka) | Schema Registry с режимом совместимости |

## Нюансы и подводные камни

- Контракт описывает то, что реально использует потребитель, а не всю схему.
- Состояния провайдера («order 42 exists») нужно уметь подготавливать в тесте провайдера.
- Проверка схем ловит структурные поломки, но не смысловые (изменение семантики поля).
- Без culture «сначала контракт» тесты становятся формальностью: включайте проверки в CI как блокирующие.

## Практика

1. Настройте Pact между фронтендом и API (или двумя сервисами) с Pact Broker.
2. Добавьте `buf breaking` и `oasdiff` в CI.
3. Смоделируйте ломающее изменение и убедитесь, что CI его блокирует.

## Вопросы с ответами

> [!question]- Что такое consumer-driven contract?
> Контракт формируется по ожиданиям потребителя; поставщик обязан их выполнять, иначе релиз блокируется.

> [!question]- Чем контрактные тесты лучше e2e для проверки интеграции?
> Быстрые, изолированные, не требуют поднимать все сервисы, локализуют поломку.

## Связанные темы

- [[N:3ea33104867981fa9871f6da12aaf8b4]]
- [[N:3ea3310486798122a480fdb4a13a418d]]
