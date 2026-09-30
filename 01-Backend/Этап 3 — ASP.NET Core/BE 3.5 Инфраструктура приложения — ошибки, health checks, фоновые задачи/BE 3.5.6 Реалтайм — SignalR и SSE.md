---
type: topic
domain: backend
stage: 3
section: "3.5"
order: 6
status: todo
level: middle
notion_id: 3ea3310486798109b98fefc0a974d817
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/realtime, topic/signalr, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Реалтайм: SignalR и SSE

↑ [[BE 3.5 Инфраструктура приложения — ошибки, health checks, фоновые задачи|3.5 Инфраструктура приложения: ошибки, health checks, фоновые задачи]] · ← [[BE 3.5.5 Graceful shutdown и жизненный цикл приложения|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















































> [!info] Зачем это на собесе
> Выбор между WebSocket, SignalR, SSE и polling по требованиям и масштабированию.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Технология | Направление | Особенности |
|---|---|---|
| Polling / long polling | клиент → сервер | просто, лишняя нагрузка |
| SSE | сервер → клиент | HTTP, авто-переподключение, только текст |
| WebSocket | двусторонний | низкий уровень, свой протокол сообщений |
| SignalR | двусторонний | абстракция: WebSocket/SSE/long polling, хабы, группы |

```csharp
public class NotificationsHub : Hub
{
    public override async Task OnConnectedAsync()
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, $"user-{Context.UserIdentifier}");
        await base.OnConnectedAsync();
    }
}

builder.Services.AddSignalR();
app.MapHub<NotificationsHub>("/hubs/notifications");

// отправка из сервиса
await hub.Clients.Group($"user-{userId}").SendAsync("orderUpdated", dto);
```

### Масштабирование

При нескольких инстансах клиенты на разных серверах не видят друг друга: нужен backplane (Redis, Azure SignalR) и sticky sessions либо только WebSocket.

### SSE

```csharp
app.MapGet("/events", (CancellationToken ct) =>
    TypedResults.ServerSentEvents(GetEvents(ct), eventType: "tick"));
```

Проще, чем SignalR, если нужен только поток от сервера (уведомления, прогресс).

## Нюансы и подводные камни

- Аутентификация WebSocket: токен в query string (для браузерного WebSocket нельзя задать заголовки) — берегите от логирования.
- Лимиты соединений и память: каждое соединение живёт долго.
- Proxy должен поддерживать Upgrade и большие таймауты.
- Сообщения не гарантируют доставку — при переподключении клиент должен запросить пропущенное.

## Практика

1. Сделайте уведомление о смене статуса заказа через SignalR.
2. Добавьте Redis backplane и запустите два инстанса.
3. Сравните SSE и SignalR для потока прогресса.

## Вопросы с ответами

> [!question]- SignalR или чистый WebSocket?
> SignalR даёт хабы, группы, fallback и переподключение; чистый WebSocket — меньше накладных, но всё вручную.

> [!question]- Когда хватит SSE?
> Когда нужен только поток от сервера к клиенту.

> [!question]- Как масштабировать SignalR?
> Backplane (Redis/Azure SignalR) и корректная настройка балансировщика.

## Связанные темы

- [[N:3ea331048679819b82adf7f42ef440d8]]
- [[N:3ea331048679811e8935f94e6640714d]]
