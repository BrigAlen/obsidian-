---
type: topic
domain: backend
stage: 5
section: "5.7"
order: 3
status: todo
level: middle
notion_id: 3ea3310486798122a480fdb4a13a418d
tags: [domain/backend, stage/5, level/middle, topic/testing, topic/grpc, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Тестирование gRPC-сервисов

↑ [[BE 5.7 Тестирование интеграций|5.7 Тестирование интеграций]] · ← [[BE 5.7.2 Контрактные тесты — Pact, проверка proto и GraphQL-схем|Предыдущая]] · → [[BE 5.7.4 Тестирование консьюмеров Kafka и очередей|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









































> [!info] Зачем это на собесе
> Как проверять gRPC-сервис от unit-уровня до интеграции.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Уровень | Как |
|---|---|
| Unit | вызвать метод сервиса напрямую с тестовым `ServerCallContext` |
| Интеграционный | `WebApplicationFactory` + `GrpcChannel.ForAddress(client.BaseAddress, new GrpcChannelOptions { HttpHandler = server.CreateHandler() })` |
| Стриминг | чтение `ResponseStream`/запись `RequestStream` |
| Ошибки | `RpcException.StatusCode` |

```csharp
public class OrdersGrpcTests(WebApplicationFactory<Program> f) : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task GetOrder_returns_NotFound_for_unknown_id()
    {
        var client = f.CreateDefaultClient();
        using var channel = GrpcChannel.ForAddress(client.BaseAddress!, new GrpcChannelOptions { HttpClient = client });
        var grpc = new OrderService.OrderServiceClient(channel);

        var ex = await Assert.ThrowsAsync<RpcException>(() => grpc.GetOrderAsync(new GetOrderRequest { Id = Guid.NewGuid().ToString() }).ResponseAsync);
        Assert.Equal(StatusCode.NotFound, ex.StatusCode);
    }
}
```

Unit-тест сервиса потребует тестовую реализацию `ServerCallContext` (например, из пакета `Grpc.Core.Testing` или собственная).

Проверяйте:

- Коды статусов и тексты ошибок, metadata.
- Deadline: сервер завершается по отмене токена.
- Стриминг: порядок, завершение, обработка отмены клиентом.
- Совместимость proto (`buf breaking`).

## Нюансы и подводные камни

- Для gRPC в тестах нужен HTTP/2: `TestServer` его поддерживает; для реального Kestrel — настройка протокола.
- Изолируйте состояние между тестами (данные, кэши).
- Тесты стриминга без таймаута зависают: задавайте `CancellationTokenSource` с лимитом.
- Аутентификацию подменяйте так же, как в HTTP-тестах.

## Практика

1. Напишите интеграционные тесты unary и server streaming.
2. Проверьте поведение при истечении deadline.
3. Добавьте тест interceptor, преобразующего исключения в статусы.

## Вопросы с ответами

> [!question]- Как тестировать gRPC без сети?
> Через `WebApplicationFactory` и канал поверх `TestServer`-обработчика.

> [!question]- Как проверить ошибку?
> Поймать `RpcException` и сравнить `StatusCode`.

## Связанные темы

- [[N:3ea33104867981028d7fdb121c3dcd02]]
- [[N:3ea3310486798180b86aeb7a4f28a1d4]]
