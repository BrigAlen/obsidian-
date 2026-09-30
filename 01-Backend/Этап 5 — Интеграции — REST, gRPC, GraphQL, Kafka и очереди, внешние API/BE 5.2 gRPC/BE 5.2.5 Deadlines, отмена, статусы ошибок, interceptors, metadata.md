---
type: topic
domain: backend
stage: 5
section: "5.2"
order: 5
status: todo
level: middle
notion_id: 3ea3310486798166a544ff42e0d3aaea
tags: [domain/backend, stage/5, level/middle, topic/api, topic/grpc, topic/reliability, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Deadlines, отмена, статусы ошибок, interceptors, metadata

↑ [[BE 5.2 gRPC|5.2 gRPC]] · ← [[BE 5.2.4 Стриминг — server, client, bidirectional|Предыдущая]] · → [[BE 5.2.6 gRPC или REST — когда что, gRPC-Web и JSON transcoding|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Про надёжность вызовов: тайм-ауты по цепочке, коды ошибок и сквозные заголовки.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Deadline** — абсолютный момент времени, к которому вызов должен завершиться. Он передаётся по цепочке сервисов (в заголовке `grpc-timeout`), поэтому вся цепочка знает оставшееся время.

```csharp
await client.GetOrderAsync(req, deadline: DateTime.UtcNow.AddSeconds(2));
// на сервере ctx.Deadline и ctx.CancellationToken; при вызове дальше передавайте ctx.CancellationToken
```

| Status code | Когда |
|---|---|
| OK | успех |
| InvalidArgument | плохой запрос |
| NotFound / AlreadyExists | ресурс |
| PermissionDenied / Unauthenticated | доступ |
| DeadlineExceeded | вышел срок |
| Unavailable | сервис недоступен (можно ретраить) |
| Internal / Unknown | ошибка сервера |
| ResourceExhausted | лимиты |

### Interceptors

Аналог middleware для gRPC:

```csharp
public class LoggingInterceptor(ILogger<LoggingInterceptor> log) : Interceptor
{
    public override async Task<TRes> UnaryServerHandler<TReq, TRes>(TReq req, ServerCallContext ctx, UnaryServerMethod<TReq, TRes> next)
    {
        try { return await next(req, ctx); }
        catch (Exception ex) { log.LogError(ex, "{Method} failed", ctx.Method); throw; }
    }
}
```

### Metadata

Заголовки вызова: `Authorization`, `X-Correlation-Id`, trace context. Читаются через `ctx.RequestHeaders`, отправляются через `Metadata`.

Ретраи настраиваются в `ServiceConfig` (`RetryPolicy` с кодами и бэкоффом) или через resilience handler.

## Нюансы и подводные камни

- Без deadline вызов может висеть вечно: задавайте всегда.
- Ретраить можно только идемпотентные вызовы и коды `Unavailable`.
- Не передавайте внутренние детали исключений клиенту.
- Метаданные — строки в нижнем регистре; бинарные ключи заканчиваются на `-bin`.

## Практика

1. Задайте deadline на клиенте и проверьте `DeadlineExceeded` на медленном сервисе.
2. Напишите interceptor, преобразующий доменные исключения в статусы.
3. Пробросьте `X-Correlation-Id` через metadata.

## Вопросы с ответами

> [!question]- Что такое deadline?
> Абсолютный срок завершения вызова; передаётся по цепочке, чтобы вложенные вызовы не превышали общий бюджет времени.

> [!question]- Что ретраить?
> Идемпотентные операции при `Unavailable`; `InvalidArgument`, `NotFound` — нет.

## Связанные темы

- [[N:3ea3310486798148ac1dc7994e831863]]
- [[N:3ea33104867981968e9cfb7e370911ab]]
