---
type: topic
domain: backend
stage: 6
section: "6.3"
order: 2
status: todo
level: junior
notion_id: 3ea33104867981238327e4f46d3f3ae1
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/orm, topic/prisma, topic/typeorm, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# TypeORM и Prisma: обзор и сравнение

↑ [[BE 6.3 ORM в Node.js — Sequelize, TypeORM, Prisma|6.3 ORM в Node.js: Sequelize, TypeORM, Prisma]] · ← [[BE 6.3.1 Sequelize — модели, ассоциации, миграции|Предыдущая]] · → [[BE 6.3.3 Работа с legacy-схемами и оптимизация запросов в ORM|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->




































> [!info] Зачем это на собесе
> Выбор ORM в Node.js: аргументированное сравнение.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Критерий | Sequelize | TypeORM | Prisma |
|---|---|---|---|
| Подход | Active Record | Data Mapper + Active Record, декораторы | схема-first + генерируемый клиент |
| Типобезопасность | слабая | средняя | сильная (типы генерируются из схемы) |
| Схема | модели в коде | сущности с декораторами | `schema.prisma` |
| Миграции | sequelize-cli | встроенные | `prisma migrate` |
| Сложные SQL | raw-запросы | QueryBuilder | `$queryRaw`, TypedSQL |
| Интеграция с Nest | `@nestjs/sequelize` | `@nestjs/typeorm` | сервис-обёртка |
| Зрелость | старый, стабильный | популярный, спорное качество | быстро растёт |

```prisma
model Order {
  id         String   @id @default(uuid())
  customerId String   @map("customer_id")
  total      Decimal  @db.Decimal(18, 2)
  customer   Customer @relation(fields: [customerId], references: [id])
  items      OrderItem[]
  @@map("orders")
}
```

```ts
const orders = await prisma.order.findMany({
  where: { total: { gt: 100 } },
  select: { id: true, customer: { select: { name: true } } },
  take: 50, orderBy: { createdAt: "desc" },
});
await prisma.$transaction([prisma.order.create({ data }), prisma.audit.create({ data: a })]);
```

Сравнение с .NET: Prisma по ощущению ближе к EF Core с проекциями; TypeORM — к NHibernate/EF классическому; сырой SQL-слой — Knex/Kysely (аналог Dapper).

## Нюансы и подводные камни

- Prisma генерирует клиент и запускает engine; учитывайте размер и особенности деплоя.
- В TypeORM ленивые связи и `synchronize: true` — источники проблем.
- Любой ORM даёт N+1: измеряйте SQL.
- Для сложной аналитики используйте SQL-билдеры (Kysely) или raw.

## Практика

1. Опишите одну и ту же модель в Prisma и TypeORM.
2. Сравните SQL, сгенерированный для одной выборки со связями.
3. Реализуйте отчёт на Kysely.

## Вопросы с ответами

> [!question]- Почему Prisma считают типобезопасной?
> Клиент генерируется из схемы, поэтому типы запросов и результатов соответствуют модели.

> [!question]- ORM или query builder?
> ORM ускоряет CRUD, query builder даёт контроль над SQL для сложных запросов.

## Связанные темы

- [[N:3ea33104867981d283b7e44ebc2a421e]]
- [[N:3ea331048679814ba3a1f8951924e9a4]]
