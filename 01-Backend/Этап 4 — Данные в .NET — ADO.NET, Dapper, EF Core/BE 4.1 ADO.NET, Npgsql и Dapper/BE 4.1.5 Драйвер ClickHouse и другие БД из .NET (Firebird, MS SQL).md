---
type: topic
domain: backend
stage: 4
section: "4.1"
order: 5
status: todo
level: middle
notion_id: 3ea331048679810c9828c6cb489c659b
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/data, topic/clickhouse, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Драйвер ClickHouse и другие БД из .NET (Firebird, MS SQL)

↑ [[BE 4.1 ADO.NET, Npgsql и Dapper|4.1 ADO.NET, Npgsql и Dapper]] · ← [[BE 4.1.4 Транзакции в .NET — DbTransaction, TransactionScope|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

























> [!info] Зачем это на собесе
> Показывает широту: в реальных проектах часто несколько СУБД. Ждут понимания, чем аналитические БД отличаются от OLTP.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| СУБД | Пакет | Замечание |
|---|---|---|
| PostgreSQL | `Npgsql` (+ `Npgsql.EntityFrameworkCore.PostgreSQL`) | основной выбор |
| MS SQL Server | `Microsoft.Data.SqlClient` | MARS, `TransactionScope` |
| ClickHouse | `ClickHouse.Client` | колоночная аналитическая БД, HTTP-интерфейс |
| Firebird | `FirebirdSql.Data.FirebirdClient` | встречается в legacy |
| MongoDB | `MongoDB.Driver` | документная |
| Redis | `StackExchange.Redis` | кэш, очереди |

### ClickHouse

Предназначен для аналитики (OLAP): огромные объёмы, агрегаты, вставка **батчами**, а не построчно; нет полноценных транзакций и эффективных `UPDATE`.

```csharp
using var conn = new ClickHouseConnection("Host=ch;Database=analytics");
await conn.OpenAsync(ct);

using var bulk = new ClickHouseBulkCopy(conn) { DestinationTableName = "events", BatchSize = 100_000 };
await bulk.InitAsync();
await bulk.WriteToServerAsync(rows, ct);

var cmd = conn.CreateCommand();
cmd.CommandText = "select toStartOfHour(ts) h, count() from events where ts > {since:DateTime} group by h";
```

### Абстракция

Общий интерфейс `IDbConnection` позволяет писать Dapper-запросы к разным БД, но диалекты SQL различаются: изолируйте доступ за репозиториями/read-моделями.

## Нюансы и подводные камни

- ClickHouse: не вставляйте по одной строке; используйте батчи или буферные таблицы/Kafka engine.
- Разные типы времени и часовые пояса между СУБД.
- Firebird: длина идентификаторов и диалект SQL; тестируйте на реальном экземпляре.
- Не тащите OLTP-паттерны (обновления по одной записи) в OLAP-хранилище.

## Практика

1. Запишите 1 млн событий в ClickHouse через `BulkCopy` и постройте агрегат по часам.
2. Подключите вторую БД и изолируйте её за интерфейсом.
3. Сравните скорость агрегата в PostgreSQL и ClickHouse на тех же данных.

## Вопросы с ответами

> [!question]- Чем ClickHouse отличается от PostgreSQL?
> Колоночное хранение для аналитики: быстрые агрегаты по большим таблицам, но слабые точечные обновления и транзакции.

> [!question]- Почему в ClickHouse вставляют батчами?
> Каждая вставка создаёт «part»; частые мелкие вставки нагружают слияния.

## Связанные темы

- [[N:3ea3310486798176ab33ccf7b823d52f]]
- [[N:3ea33104867981c7a0d3ffbde71096db]]
