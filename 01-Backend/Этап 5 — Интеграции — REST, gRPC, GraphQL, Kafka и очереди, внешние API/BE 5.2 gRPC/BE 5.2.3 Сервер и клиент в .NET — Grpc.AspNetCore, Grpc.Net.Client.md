---
type: topic
domain: backend
stage: 5
section: "5.2"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981d8a167cf3156da316c
tags: [domain/backend, stage/5, level/middle, topic/api, topic/grpc, topic/dotnet, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Сервер и клиент в .NET: Grpc.AspNetCore, Grpc.Net.Client

↑ [[BE 5.2 gRPC|5.2 gRPC]] · ← [[BE 5.2.2 Protobuf — proto-контракты, типы, эволюция схем|Предыдущая]] · → [[BE 5.2.4 Стриминг — server, client, bidirectional|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
































> [!info] Зачем это на собесе
> Практическая часть: как поднять gRPC-сервис и вызывать его из другого сервиса.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### Сервер

```csharp
// Program.cs
builder.Services.AddGrpc(o => o.Interceptors.Add<ExceptionInterceptor>());
app.MapGrpcService<OrderGrpcService>();

public class OrderGrpcService(IOrderService orders) : OrderService.OrderServiceBase
{
    public override async Task<OrderReply> GetOrder(GetOrderRequest req, ServerCallContext ctx)
    {
        var order = await orders.FindAsync(Guid.Parse(req.Id), ctx.CancellationToken)
            ?? throw new RpcException(new Status(StatusCode.NotFound, "order not found"));
        return new OrderReply { Id = order.Id.ToString(), Customer = order.Customer };
    }
}
```

### Клиент

```csharp
builder.Services.AddGrpcClient<OrderService.OrderServiceClient>(o => o.Address = new Uri("https://orders:8443"))
    .AddStandardResilienceHandler();

public class Checkout(OrderService.OrderServiceClient client)
{
    public async Task<OrderReply> LoadAsync(string id, CancellationToken ct)
        => await client.GetOrderAsync(new GetOrderRequest { Id = id }, deadline: DateTime.UtcNow.AddSeconds(3), cancellationToken: ct);
}
```

`AddGrpcClient` использует `HttpClientFactory`: пул соединений и ретраи настраиваются так же. Внутри сети без TLS используйте h2c (`Http2UnencryptedSupport`).

## Нюансы и подводные камни

- Сервис gRPC создаётся на вызов (transient); состояние храните в DI, не в полях.
- Исключения превращайте в `RpcException` с корректным `StatusCode` в interceptor.
- Клиент должен передавать `CancellationToken` и deadline.
- Kestrel: HTTP/2 требует TLS или явной настройки `Http2` для порта.
- Модели protobuf — не доменные: маппьте их на границе.

## Практика

1. Поднимите gRPC-сервис и клиент в двух проектах.
2. Добавьте interceptor для логирования и преобразования исключений.
3. Включите gRPC reflection и проверьте через `grpcurl`.

## Вопросы с ответами

> [!question]- Как в gRPC вернуть ошибку?
> Бросить `RpcException` с `StatusCode` и сообщением/метаданными.

> [!question]- Нужно ли создавать канал на каждый вызов?
> Нет: канал переиспользуют (через `AddGrpcClient` или singleton).

## Связанные темы

- [[N:3ea33104867981be87bad18634612698]]
- [[N:3ea3310486798148ac1dc7994e831863]]
