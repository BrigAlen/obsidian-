---
type: topic
domain: backend
stage: 1
section: "1.1"
order: 5
status: todo
level: junior
notion_id: 3ea33104867981bb8a3cd70eff7d424c
tags: [backend, stage-1, networks, api]
rewritten: true
reviewed:
next_review:
---

# Стили API: REST, RPC, GraphQL, WebSocket, SSE

↑ [[BE 1.1 Сети и протоколы для бэкенда|1.1 Сети и протоколы для бэкенда]] · ← [[BE 1.1.4 DNS, балансировка, reverse proxy|Предыдущая]]

> [!note] Переписано
> В Notion эта страница содержала шаблонный текст без отношения к теме. Здесь — содержательная версия.

> [!info] Зачем это на собесе
> «Как бы вы сделали API?» — стартовый вопрос почти любого интервью. Нужно уметь выбрать стиль под задачу и объяснить компромиссы: REST для публичных CRUD-API, gRPC между сервисами, GraphQL для гибких клиентских выборок, WebSocket и SSE для push.

## Подтемы
- [ ] REST: ресурсы, HATEOAS, ограничения
- [ ] RPC и gRPC
- [ ] GraphQL
- [ ] WebSocket
- [ ] SSE (Server-Sent Events)
- [ ] Как выбрать стиль

## Объяснение

### Сравнение
| Стиль | Транспорт | Формат | Направление | Сильная сторона | Слабая сторона |
|---|---|---|---|---|---|
| REST | HTTP/1.1+ | JSON | запрос → ответ | простота, кэш, инструменты | over/under-fetching, много запросов |
| gRPC | HTTP/2 | Protobuf | запрос-ответ + стримы | скорость, строгие контракты, codegen | не работает напрямую из браузера (нужен gRPC-Web), сложнее отладка |
| GraphQL | HTTP (POST) | JSON | запрос → ответ (+ subscriptions) | клиент сам выбирает поля, один endpoint | N+1, сложный кэш и авторизация на полях, защита от тяжёлых запросов |
| WebSocket | TCP (upgrade из HTTP) | любой | двусторонний | низкая задержка, полный дуплекс | stateful, масштабирование и балансировка сложнее |
| SSE | HTTP | текст (`text/event-stream`) | сервер → клиент | просто, авто-реконнект, работает через HTTP | только в одну сторону, лимит соединений в HTTP/1.1 |

### REST
- Ресурсы — существительные (`/patients/42/visits`), действие задаёт метод HTTP.
- Stateless: каждый запрос самодостаточен, состояние сессии не на сервере.
- Единообразие: коды статусов, форматы ошибок (ProblemDetails), пагинация, фильтры.
- Уровни зрелости Ричардсона: ресурсы → HTTP-методы → HATEOAS (гиперссылки, на практике редко).

### RPC / gRPC
- Вызов удалённой процедуры: `GetPatient(id)`, а не «GET ресурса».
- gRPC: контракт в `.proto`, Protobuf компактнее JSON, HTTP/2 мультиплексирует, есть unary, server/client/bidirectional streaming, deadlines и отмена.
- Идеально для внутренней связи микросервисов.

### GraphQL
- Одна точка входа, клиент описывает нужную форму ответа.
- Схема со строгой типизацией; query, mutation, subscription.
- Риски: N+1 (лечат DataLoader), «дорогие» запросы (лимиты глубины и сложности), кэширование сложнее HTTP-кэша.

### WebSocket
- Начинается как HTTP-запрос с `Upgrade: websocket`, затем это двусторонний поток фреймов поверх одного TCP.
- Чаты, котировки, совместное редактирование. В .NET — SignalR (автоматически выбирает транспорт и переподключается).

### SSE
- Обычный HTTP-ответ, который не закрывается: `Content-Type: text/event-stream`.
- Формат: строки `data: ...` и пустая строка между событиями; `id:` для `Last-Event-ID` при реконнекте.
- Подходит для лент уведомлений, прогресса задач, стриминга ответов LLM.

## Примеры
```csharp
// REST: Minimal API
app.MapGet("/api/patients/{id:guid}", async (Guid id, IPatientService svc, CancellationToken ct) =>
    await svc.FindAsync(id, ct) is { } p ? Results.Ok(p) : Results.NotFound());
```
```csharp
// SSE в ASP.NET Core (.NET 10: TypedResults.ServerSentEvents; до этого — вручную)
app.MapGet("/api/jobs/{id}/events", async (string id, HttpContext ctx, IJobEvents events, CancellationToken ct) =>
{
    ctx.Response.Headers.ContentType = "text/event-stream";
    await foreach (var e in events.SubscribeAsync(id, ct))
    {
        await ctx.Response.WriteAsync($"id: {e.Id}\ndata: {e.Json}\n\n", ct);
        await ctx.Response.Body.FlushAsync(ct);
    }
});
```
```csharp
// WebSocket через SignalR
public class ChatHub : Hub
{
    public Task Send(string room, string text) =>
        Clients.Group(room).SendAsync("message", Context.UserIdentifier, text);
}
```
```proto
// gRPC контракт
service Patients { rpc Get (GetPatientRequest) returns (Patient); }
```

## Нюансы и подводные камни
- WebSocket и SSE держат соединения открытыми: nginx нужны `proxy_http_version 1.1`, заголовки `Upgrade`/`Connection` (для WS), `proxy_buffering off` (для SSE) и большие `proxy_read_timeout`.
- За L7-балансировщиком WebSocket требует sticky-сессий или общего backplane (Redis) для SignalR при нескольких инстансах.
- В HTTP/1.1 браузер разрешает ~6 соединений на домен — несколько SSE-потоков могут исчерпать лимит; HTTP/2 снимает проблему.
- gRPC из браузера — только gRPC-Web с прокси (Envoy).
- Не выбирайте GraphQL «потому что модно»: для простого CRUD REST дешевле в поддержке.

## Как выбрать
- Публичный API для внешних клиентов, кэш и простота → **REST**.
- Быстрая внутренняя связь между сервисами, стриминг → **gRPC**.
- Много разнородных клиентов с разными потребностями в данных → **GraphQL** (часто как BFF-слой).
- Двусторонний realtime → **WebSocket/SignalR**.
- Односторонние уведомления → **SSE**.

## Вопросы с ответами
> [!question]- Чем REST отличается от RPC?
> REST ориентирован на ресурсы и единообразные операции HTTP, RPC — на вызов действий (процедур). REST лучше кэшируется и понятнее публичным клиентам, RPC (gRPC) быстрее и строже типизирован.

> [!question]- Когда WebSocket, а когда SSE?
> SSE — если данные идут только с сервера на клиента (уведомления, прогресс): проще, работает поверх обычного HTTP, есть авто-реконнект. WebSocket — если нужен двусторонний обмен с низкой задержкой (чат, игры, совместное редактирование).

> [!question]- Какие проблемы у GraphQL на бэкенде?
> N+1 при разрешении полей (DataLoader/batching), защита от слишком глубоких и дорогих запросов, сложное HTTP-кэширование, авторизация на уровне полей.

> [!question]- Почему gRPC не вызвать напрямую из браузера?
> Браузер не даёт нужного контроля над HTTP/2-фреймами и trailers. Используют gRPC-Web через прокси или REST/GraphQL-шлюз.

> [!question]- Что нужно настроить в nginx для SSE и WebSocket?
> `proxy_http_version 1.1`, для WS — `Upgrade` и `Connection: upgrade`, для SSE — `proxy_buffering off`, а также увеличить `proxy_read_timeout`, иначе прокси оборвёт «молчащее» соединение.

## Связанные темы
- Предыдущая: [[N:3ea331048679817aa584c01ff29564d5]]
- REST-дизайн: [[N:3ea331048679815bbaf8cf164556ce50]]
- gRPC: [[N:3ea3310486798179a13ffc9e7cbe426f]]
- GraphQL на бэкенде: [[N:3ea3310486798129b2f2f59ce40dd5b9]]
- WebSocket, SSE и gRPC через Nginx: [[N:9236fc85d1dc460fbe8ba17be6ac68ca]]
