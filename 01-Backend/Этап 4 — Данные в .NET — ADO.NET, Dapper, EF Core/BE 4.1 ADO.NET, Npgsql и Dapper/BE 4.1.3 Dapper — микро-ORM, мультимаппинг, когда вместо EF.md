---
type: topic
domain: backend
stage: 4
section: "4.1"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981008e07e7e6edb5cbc2
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/data, topic/dapper, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Dapper: микро-ORM, мультимаппинг, когда вместо EF

↑ [[BE 4.1 ADO.NET, Npgsql и Dapper|4.1 ADO.NET, Npgsql и Dapper]] · ← [[BE 4.1.2 Параметризованные запросы и SQL-инъекции|Предыдущая]] · → [[BE 4.1.4 Транзакции в .NET — DbTransaction, TransactionScope|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
























> [!info] Зачем это на собесе
> «Dapper или EF Core?» — вопрос на компромиссы. Хороший ответ: разные инструменты, часто вместе.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Dapper — набор extension-методов над `IDbConnection`: выполняет SQL и мапит результат в объекты. Нет change tracking, LINQ и миграций.

```csharp
var users = await conn.QueryAsync<User>(
    "select id, name from users where created > @since", new { since });

var one = await conn.QuerySingleOrDefaultAsync<User>("select * from users where id = @id", new { id });
await conn.ExecuteAsync("update users set name = @name where id = @id", new { id, name });

// IN со списком
var items = await conn.QueryAsync<Item>("select * from items where id = any(@ids)", new { ids });
```

### Multi-mapping

```csharp
var orders = await conn.QueryAsync<Order, Customer, Order>(
    "select o.*, c.* from orders o join customers c on c.id = o.customer_id",
    (o, c) => { o.Customer = c; return o; },
    splitOn: "id");
```

`splitOn` указывает, с какой колонки начинается следующий объект.

### QueryMultiple

```csharp
using var grid = await conn.QueryMultipleAsync(sql, args);
var orders = await grid.ReadAsync<Order>();
var total  = await grid.ReadSingleAsync<int>();
```

| Критерий | Dapper | EF Core |
|---|---|---|
| Скорость и контроль SQL | максимум | хорошо при правильном использовании |
| Скорость разработки CRUD | ниже | выше |
| Миграции, change tracking | нет | да |
| Сложные отчёты и raw SQL | удобно | возможно |

Типичная схема: EF Core для записи и доменной модели, Dapper для быстрых read-запросов.

## Нюансы и подводные камни

- `snake_case` колонок: `DefaultTypeMap.MatchNamesWithUnderscores = true`.
- Мультимаппинг с неверным `splitOn` даёт пустые объекты.
- Не открывайте соединение вручную без `using`; Dapper сам откроет закрытое, но не закроет открытое.
- `AddWithValue`-подобная типизация: для `Guid`, `DateOnly` могут понадобиться `TypeHandler`.
- Нет защиты от N+1: проектируйте запросы сами.

## Практика

1. Реализуйте read-модель списка заказов на Dapper с join-ами.
2. Настройте маппинг snake_case.
3. Сравните скорость чтения 10 000 строк в EF Core (AsNoTracking) и Dapper.

## Вопросы с ответами

> [!question]- Когда Dapper лучше EF?
> Для сложных read-запросов, отчётов, критичных по скорости мест и когда нужен полный контроль над SQL.

> [!question]- Можно ли использовать вместе?
> Да, при общем соединении/транзакции: EF для записи, Dapper для чтения.

> [!question]- Что такое splitOn?
> Название колонки, с которой Dapper начинает мапить следующий тип при мультимаппинге.

## Связанные темы

- [[N:3ea3310486798158868ffb2e607fee11]]
- [[N:3ea3310486798176ab33ccf7b823d52f]]
