---
type: topic
domain: backend
stage: 5
section: "5.2"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981be87bad18634612698
tags: [domain/backend, stage/5, level/middle, topic/api, topic/grpc, topic/protobuf, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Protobuf: proto-контракты, типы, эволюция схем

↑ [[BE 5.2 gRPC|5.2 gRPC]] · ← [[BE 5.2.1 gRPC и HTTP-2 — как работает|Предыдущая]] · → [[BE 5.2.3 Сервер и клиент в .NET — Grpc.AspNetCore, Grpc.Net.Client|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















> [!info] Зачем это на собесе
> Как менять контракт gRPC/Kafka, не ломая клиентов: номера полей, reserved, обратная совместимость.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```protobuf
syntax = "proto3";
option csharp_namespace = "Orders.Contracts";

service OrderService {
  rpc GetOrder (GetOrderRequest) returns (OrderReply);
  rpc Watch (WatchRequest) returns (stream OrderEvent);
}

message GetOrderRequest { string id = 1; }

message OrderReply {
  string id = 1;
  string customer = 2;
  repeated Item items = 3;
  google.protobuf.Timestamp created_at = 4;
  Status status = 5;
  reserved 6, 7;             // удалённые поля
  reserved "old_name";
}

enum Status { STATUS_UNSPECIFIED = 0; NEW = 1; PAID = 2; }
```

| Тип proto | C# |
|---|---|
| `int32/int64`, `uint32` | `int`, `long`, `uint` |
| `double`, `float`, `bool`, `string`, `bytes` | одноимённые / `ByteString` |
| `repeated T` | `RepeatedField<T>` |
| `map<K,V>` | `MapField<K,V>` |
| `google.protobuf.Timestamp/Duration` | `Timestamp`, `Duration` (конвертация в `DateTime`) |
| `oneof` | взаимоисключающие поля |
| `optional` | различает «не задано» и значение по умолчанию |

### Эволюция схемы

Безопасно: добавлять новые поля с новыми номерами, добавлять значения enum, менять имена полей (по сети идут номера).
Опасно: менять номер или тип поля, переиспользовать удалённый номер, менять `repeated`/скаляр.
Удаляя поле, помечайте его `reserved`.

## Нюансы и подводные камни

- В proto3 у скаляров нет `null`: значение по умолчанию (0, "", false) неотличимо от «не задано» без `optional`.
- Первое значение enum должно быть `0` (`UNSPECIFIED`).
- Деньги не храните в `double`: `string`/`int64` в минимальных единицах или `Money`-сообщение.
- Ошибки контракта лучше ловить проверками совместимости (`buf breaking`).

## Практика

1. Опишите контракт заказов и сгенерируйте C#-код.
2. Добавьте поле, затем удалите его с `reserved`, проверьте совместимость `buf breaking`.
3. Используйте `oneof` для разных способов оплаты.

## Вопросы с ответами

> [!question]- Почему нельзя менять номера полей?
> В бинарном формате поле идентифицируется номером; смена сломает десериализацию у старых клиентов.

> [!question]- Что делает reserved?
> Запрещает повторное использование номеров/имён удалённых полей.

> [!question]- Как различить 0 и «не задано» в proto3?
> Использовать `optional` или wrapper-типы.

## Связанные темы

- [[N:3ea33104867981f3b15bfe79b76ee3cc]]
- [[N:3ea33104867981d8a167cf3156da316c]]
