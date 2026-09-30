---
type: topic
domain: db
stage: 4
section: "4.1"
order: 5
status: todo
level: middle
notion_id: 3ea3310486798121a10ef0353ac81834
tags: [domain/db, stage/4, level/middle, topic/mongodb, topic/nosql, topic/documents, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# MongoDB: документная модель, индексы, агрегации (обзорно)

↑ [[DB 4.1 Redis и MongoDB|4.1 Redis и MongoDB]] · ← [[DB 4.1.4 Redis — persistence, репликация, Sentinel, Cluster|Предыдущая]] · → [[DB 4.1.6 SQL или NoSQL — как выбрать|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Достаточно понимать, когда документная БД подходит и как она отличается от реляционной.

## Документная модель

Данные хранятся как **документы** (BSON, надмножество JSON) в **коллекциях**. Схема гибкая (schema-on-read), но можно задать валидацию (`$jsonSchema`).

```json
{
  "_id": { "$oid": "66f1c0..." },
  "email": "anna@example.com",
  "name": "Анна",
  "address": { "city": "Москва", "zip": "101000" },
  "orders": [ { "id": 1, "total": 1500, "items": ["book", "pen"] } ],
  "tags": ["vip", "beta"]
}
```

Лимит документа — 16 МБ.

## Моделирование: встраивать или ссылаться

| Подход | Когда |
|---|---|
| **Embed** (вложить) | данные читаются вместе, связь 1:few, вложенные ограничены по размеру |
| **Reference** (ссылка по `_id`) | связь 1:many / many:many, большие или часто изменяемые данные, нужен независимый доступ |
| **Гибрид** | вложить часть полей (снимок) + ссылка на полную сущность |

Принцип: **проектируйте под запросы** (данные, которые читаются вместе, хранятся вместе). Избегайте неограниченно растущих массивов.

## CRUD

```javascript
db.users.insertOne({ name: "Анна", email: "anna@example.com" })
db.users.find({ "address.city": "Москва", tags: "vip" }, { name: 1, email: 1 }).sort({ name: 1 }).limit(20)
db.users.updateOne({ _id }, { $set: { name: "Анна П." }, $inc: { logins: 1 }, $push: { tags: "pro" } })
db.users.deleteMany({ inactive: true })
db.users.updateOne({ email }, { $setOnInsert: { createdAt: new Date() }, $set: { seen: new Date() } }, { upsert: true })
```

Операторы: `$eq`, `$gt`, `$in`, `$and/$or`, `$exists`, `$regex`, `$elemMatch`, `$set`, `$unset`, `$inc`, `$push`, `$pull`, `$addToSet`.

## Индексы

```javascript
db.users.createIndex({ email: 1 }, { unique: true })
db.orders.createIndex({ customerId: 1, createdAt: -1 })     // составной
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })   // TTL-индекс
db.logs.createIndex({ status: 1 }, { partialFilterExpression: { status: "error" } })
db.articles.createIndex({ title: "text", body: "text" })    // текстовый
db.places.createIndex({ location: "2dsphere" })             // гео
db.orders.find({ ... }).explain("executionStats")            // план и статистика
```

Правила аналогичны реляционным: порядок в составных индексах, покрывающие запросы, лишние индексы замедляют запись. **ESR-правило**: сначала Equality, затем Sort, затем Range.

## Aggregation Pipeline

```javascript
db.orders.aggregate([
  { $match: { status: "paid", createdAt: { $gte: ISODate("2026-01-01") } } },
  { $group: { _id: "$customerId", revenue: { $sum: "$total" }, orders: { $sum: 1 } } },
  { $sort: { revenue: -1 } },
  { $limit: 10 },
  { $lookup: { from: "customers", localField: "_id", foreignField: "_id", as: "customer" } },
  { $unwind: "$customer" },
  { $project: { _id: 0, email: "$customer.email", revenue: 1, orders: 1 } }
])
```

Этапы: `$match`, `$group`, `$project`, `$sort`, `$limit`, `$unwind`, `$lookup` (аналог JOIN), `$facet`, `$bucket`, `$merge`. `$match` и `$project` ставьте раньше, чтобы использовать индексы.

## Транзакции и согласованность

- операции над одним документом атомарны;
- **многодокументные транзакции ACID** (с версии 4.0/4.2, в replica set и шардах): дороже, используйте умеренно;
- `writeConcern` (`w: "majority"`), `readConcern`, `readPreference`.

## Масштабирование

- **Replica Set**: первичный узел + вторичные, автоматические выборы; чтение со вторичных с задержкой;
- **Sharding**: шардирование по ключу (хэш или диапазон) через `mongos` и config-серверы; выбор shard key критичен (кардинальность, распределение, отсутствие монотонности).

## Использование из .NET

Драйвер `MongoDB.Driver`: `IMongoCollection<T>`, LINQ, `Builders<T>`, маппинг классов (`BsonId`, `BsonElement`).

## Ограничения

Нет надёжных JOIN (только `$lookup`, дорогой), связи и целостность на приложении, дублирование данных, схема «без схемы» приводит к хаосу без дисциплины.

## Вопросы с ответами

> [!question]- Когда встраивать данные в документ, а когда ссылаться?
> Встраивать — если данные читаются вместе, связь один-к-немногим и вложение не растёт бесконечно. Ссылаться — при связях один-ко-многим и многие-ко-многим, больших или часто изменяемых данных.

> [!question]- Поддерживает ли MongoDB транзакции?
> Да, ACID-транзакции над несколькими документами (replica set и sharded cluster), но их лучше избегать за счёт правильной модели: операции над одним документом атомарны.

> [!question]- Что такое ESR-правило?
> Порядок полей в составном индексе: Equality (равенство), Sort (сортировка), Range (диапазон).
