---
type: topic
domain: backend
stage: 4
section: "4.1"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798176ab33ccf7b823d52f
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/data, topic/transactions, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Транзакции в .NET: DbTransaction, TransactionScope

↑ [[BE 4.1 ADO.NET, Npgsql и Dapper|4.1 ADO.NET, Npgsql и Dapper]] · ← [[BE 4.1.3 Dapper — микро-ORM, мультимаппинг, когда вместо EF|Предыдущая]] · → [[BE 4.1.5 Драйвер ClickHouse и другие БД из .NET (Firebird, MS SQL)|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->











> [!info] Зачем это на собесе
> Про ACID на уровне кода: где границы транзакции и почему TransactionScope + async опасен.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```csharp
await using var conn = await dataSource.OpenConnectionAsync(ct);
await using var tx = await conn.BeginTransactionAsync(IsolationLevel.ReadCommitted, ct);
try
{
    await conn.ExecuteAsync("update accounts set balance = balance - @a where id = @from", new { a, from }, tx);
    await conn.ExecuteAsync("update accounts set balance = balance + @a where id = @to",   new { a, to }, tx);
    await tx.CommitAsync(ct);
}
catch
{
    await tx.RollbackAsync(ct);
    throw;
}
```

### TransactionScope

```csharp
using var scope = new TransactionScope(TransactionScopeOption.Required,
    new TransactionOptions { IsolationLevel = IsolationLevel.ReadCommitted },
    TransactionScopeAsyncFlowOption.Enabled);   // обязателен для async
// ... операции нескольких вызовов...
scope.Complete();
```

Неявно привлекает все соединения в «ambient» транзакцию. Несколько разных соединений/БД → эскалация до распределённой (MSDTC), что в .NET Core на Linux неподдерживаемо и не рекомендуется.

| Уровень изоляции | Аномалии, которые возможны |
|---|---|
| Read Uncommitted | грязное чтение (в PG = Read Committed) |
| Read Committed | неповторяемое чтение, фантомы |
| Repeatable Read | фантомы (в PG — нет, snapshot) |
| Serializable | нет; возможны ошибки сериализации, нужен retry |

### EF Core

`SaveChanges` уже выполняется в транзакции. Явная: `db.Database.BeginTransactionAsync()`; стратегия повторов (`EnableRetryOnFailure`) требует оборачивать транзакции в `CreateExecutionStrategy().ExecuteAsync`.

## Нюансы и подводные камни

- Держите транзакцию короткой: не вызывайте внешний HTTP внутри.
- Без `TransactionScopeAsyncFlowOption.Enabled` в async-коде получите исключение или потерю транзакции.
- Между сервисами и БД распределённые транзакции заменяют сага и outbox (см. этап 8).
- При deadlock/serialization failure — повторяйте транзакцию целиком.
- Забытый `Complete()` = откат.

## Практика

1. Реализуйте перевод денег с откатом при ошибке.
2. Воспроизведите неповторяемое чтение на двух сессиях psql.
3. Обработайте serialization failure ретраем.

## Вопросы с ответами

> [!question]- Что такое ACID?
> Атомарность, согласованность, изолированность, долговечность.

> [!question]- Чем плох TransactionScope?
> Неявность и риск распределённых транзакций; в async нужен `AsyncFlowOption.Enabled`.

> [!question]- Какой уровень изоляции по умолчанию в PostgreSQL?
> Read Committed.

## Связанные темы

- [[N:3ea33104867981008e07e7e6edb5cbc2]]
- [[N:3ea331048679810c9828c6cb489c659b]]
