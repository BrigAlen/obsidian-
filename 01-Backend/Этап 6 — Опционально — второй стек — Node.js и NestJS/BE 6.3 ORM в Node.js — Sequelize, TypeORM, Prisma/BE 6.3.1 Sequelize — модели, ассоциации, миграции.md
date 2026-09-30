---
type: topic
domain: backend
stage: 6
section: "6.3"
order: 1
status: todo
level: junior
notion_id: 3ea33104867981d283b7e44ebc2a421e
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/orm, topic/sequelize, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Sequelize: модели, ассоциации, миграции

↑ [[BE 6.3 ORM в Node.js — Sequelize, TypeORM, Prisma|6.3 ORM в Node.js: Sequelize, TypeORM, Prisma]] · → [[BE 6.3.2 TypeORM и Prisma — обзор и сравнение|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Sequelize встречается в legacy Node.js-проектах; ждут понимания моделей, связей и миграций.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Sequelize — ORM на паттерне Active Record/Data Mapper для PostgreSQL, MySQL, MSSQL, SQLite.

```ts
class Order extends Model<InferAttributes<Order>, InferCreationAttributes<Order>> {
  declare id: CreationOptional<string>;
  declare customerId: string;
  declare total: number;
}
Order.init({
  id: { type: DataTypes.UUID, defaultValue: DataTypes.UUIDV4, primaryKey: true },
  customerId: { type: DataTypes.UUID, allowNull: false, field: "customer_id" },
  total: { type: DataTypes.DECIMAL(18, 2), allowNull: false },
}, { sequelize, tableName: "orders", underscored: true });

Customer.hasMany(Order, { foreignKey: "customerId", as: "orders" });
Order.belongsTo(Customer, { foreignKey: "customerId", as: "customer" });
Order.belongsToMany(Product, { through: OrderItem });

const orders = await Order.findAll({
  where: { total: { [Op.gt]: 100 } },
  include: [{ model: Customer, as: "customer", attributes: ["name"] }],
  order: [["createdAt", "DESC"]], limit: 50,
});
```

Миграции — файлы `up/down` через `sequelize-cli` и `queryInterface`; история в таблице `SequelizeMeta`. Транзакции: `sequelize.transaction(async (t) => { await Order.create({...}, { transaction: t }); })`.

## Нюансы и подводные камни

- `include` нескольких коллекций порождает декартово произведение (аналог cartesian explosion в EF); `separate: true` или отдельные запросы.
- Забытый `transaction` в вызове выполняет запрос вне транзакции.
- `sync({ alter: true })` в продакшене недопустим: схема — только через миграции.
- Ленивая загрузка отсутствует: связи грузятся явно.
- Типизация TypeScript «неродная»: возможно расхождение типов и схемы.

## Практика

1. Опишите модели заказов/клиентов/позиций и связи.
2. Напишите миграцию добавления колонки с индексом.
3. Найдите и исправьте N+1 через `include`.

## Вопросы с ответами

> [!question]- Как в Sequelize управлять схемой?
> Миграциями (`up`/`down`), а не `sync`.

> [!question]- Как избежать N+1?
> Жадная загрузка `include` или пакетные запросы.

## Связанные темы

- [[N:3ea33104867981eab321da100aae4744]]
- [[N:3ea33104867981238327e4f46d3f3ae1]]
