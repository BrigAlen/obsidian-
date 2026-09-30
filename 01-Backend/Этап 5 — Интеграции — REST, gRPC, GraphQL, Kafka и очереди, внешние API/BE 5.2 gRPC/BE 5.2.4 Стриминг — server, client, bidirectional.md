---
type: topic
domain: backend
stage: 5
section: "5.2"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798148ac1dc7994e831863
tags: [domain/backend, stage/5, level/middle, topic/api, topic/grpc, topic/streaming, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Стриминг: server, client, bidirectional

↑ [[BE 5.2 gRPC|5.2 gRPC]] · ← [[BE 5.2.3 Сервер и клиент в .NET — Grpc.AspNetCore, Grpc.Net.Client|Предыдущая]] · → [[BE 5.2.5 Deadlines, отмена, статусы ошибок, interceptors, metadata|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



























> [!info] Зачем это на собесе
> Когда gRPC-стриминг оправдан и как правильно завершать поток.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Вид | proto | Пример |
|---|---|---|
| Unary | `rpc A (Req) returns (Res)` | обычный запрос |
| Server streaming | `returns (stream Res)` | подписка на события, выгрузка |
| Client streaming | `(stream Req) returns (Res)` | загрузка файла кусками |
| Bidirectional | `(stream Req) returns (stream Res)` | чат, телеметрия |

```csharp
// Server streaming
public override async Task Watch(WatchRequest req, IServerStreamWriter<OrderEvent> stream, ServerCallContext ctx)
{
    await foreach (var e in events.SubscribeAsync(ctx.CancellationToken))
        await stream.WriteAsync(new OrderEvent { Id = e.Id });
}

// Client
using var call = client.Watch(new WatchRequest());
await foreach (var e in call.ResponseStream.ReadAllAsync(ct))
    Console.WriteLine(e.Id);

// Client streaming
using var upload = client.Upload();
foreach (var chunk in chunks) await upload.RequestStream.WriteAsync(chunk);
await upload.RequestStream.CompleteAsync();
var result = await upload;
```

## Нюансы и подводные камни

- Стрим держит соединение: планируйте keepalive и переподключение.
- Обрабатывайте `ctx.CancellationToken`, иначе поток продолжит работать после ухода клиента.
- Обратное давление: медленный клиент замедляет `WriteAsync`; ограничивайте очередь.
- Запись в один стрим из нескольких потоков одновременно недопустима.
- Между балансировщиками длинные стримы могут обрываться: делайте idle-timeout и retry.

## Практика

1. Реализуйте загрузку файла клиентским стримом по 64 КБ.
2. Сделайте server streaming уведомлений с переподключением клиента.
3. Соберите чат на bidirectional streaming.

## Вопросы с ответами

> [!question]- Когда использовать streaming, а не unary?
> Для больших/бесконечных потоков и событий, чтобы не буферизовать всё в одном сообщении.

> [!question]- Что происходит при отмене клиентом?
> Срабатывает `ServerCallContext.CancellationToken`; сервер должен прекратить работу.

## Связанные темы

- [[N:3ea33104867981d8a167cf3156da316c]]
- [[N:3ea3310486798166a544ff42e0d3aaea]]
