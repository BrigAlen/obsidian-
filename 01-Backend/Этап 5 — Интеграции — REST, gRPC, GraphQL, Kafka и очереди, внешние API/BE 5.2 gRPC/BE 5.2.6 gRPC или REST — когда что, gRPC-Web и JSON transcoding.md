---
type: topic
domain: backend
stage: 5
section: "5.2"
order: 6
status: todo
level: middle
notion_id: 3ea33104867981968e9cfb7e370911ab
tags: [domain/backend, stage/5, level/middle, topic/api, topic/grpc, topic/rest, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# gRPC или REST: когда что, gRPC-Web и JSON transcoding

↑ [[BE 5.2 gRPC|5.2 gRPC]] · ← [[BE 5.2.5 Deadlines, отмена, статусы ошибок, interceptors, metadata|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




























> [!info] Зачем это на собесе
> Выбор технологии обмена — типичный архитектурный вопрос.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Критерий | gRPC | REST/JSON |
|---|---|---|
| Производительность | выше | ниже |
| Контракт | строгий (proto) | необязательный (OpenAPI) |
| Стриминг | встроен | SSE/WebSocket |
| Браузер | через gRPC-Web/transcoding | нативно |
| Отладка | сложнее | curl, браузер |
| Кэширование HTTP | нет | да |
| Публичный API | редко | стандарт |
| Меж-сервисный обмен | отлично | нормально |

**Практика:** REST/JSON — наружу (браузеры, партнёры), gRPC — между внутренними сервисами и там, где нужны стриминг и строгие контракты.

- **gRPC-Web**: подмножество gRPC для браузера через прокси (Envoy) или middleware `UseGrpcWeb`; нет client/bidirectional стриминга.
- **JSON transcoding** (`Microsoft.AspNetCore.Grpc.JsonTranscoding`): один сервис отдаёт и gRPC, и REST/JSON по аннотациям `google.api.http`; генерируется OpenAPI.

```protobuf
rpc GetOrder (GetOrderRequest) returns (OrderReply) {
  option (google.api.http) = { get: "/v1/orders/{id}" };
}
```

## Нюансы и подводные камни

- «gRPC быстрее» важно, лишь если узкое место в сериализации/сети, иначе выигрыш незаметен.
- Двойной API (gRPC + REST) требует единого контракта; transcoding помогает избежать дублирования.
- Инструменты и опыт команды — тоже критерии.
- GraphQL — третий вариант для гибких клиентских запросов (см. [[N:3ea3310486798175b3a6d2f428a4a9d4]]).

## Практика

1. Опишите критерии выбора для вашего проекта в ADR.
2. Включите JSON transcoding и проверьте REST-вызов того же метода.
3. Сравните три протокола под нагрузкой.

## Вопросы с ответами

> [!question]- Когда gRPC, а когда REST?
> gRPC — межсервисно, стриминг, строгий контракт; REST — публичные API и браузеры.

> [!question]- Что такое JSON transcoding?
> Отдача gRPC-методов как REST/JSON endpoint-ов по аннотациям в proto.

## Связанные темы

- [[N:3ea3310486798166a544ff42e0d3aaea]]
- [[N:3ea3310486798175b3a6d2f428a4a9d4]]
