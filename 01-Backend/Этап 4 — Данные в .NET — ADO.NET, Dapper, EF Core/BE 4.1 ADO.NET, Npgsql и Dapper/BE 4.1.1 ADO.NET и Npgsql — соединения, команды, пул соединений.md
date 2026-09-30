---
type: topic
domain: backend
stage: 4
section: "4.1"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981a48a67fbad9002cd95
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/data, topic/adonet, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# ADO.NET и Npgsql: соединения, команды, пул соединений

↑ [[BE 4.1 ADO.NET, Npgsql и Dapper|4.1 ADO.NET, Npgsql и Dapper]] · → [[BE 4.1.2 Параметризованные запросы и SQL-инъекции|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






































> [!info] Зачем это на собесе
> Вопросы про пул соединений и утечки соединений — классика. Они показывают, понимаете ли вы, что находится под ORM.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

ADO.NET — базовый слой доступа к данным в .NET. Провайдер (Npgsql для PostgreSQL, Microsoft.Data.SqlClient для SQL Server) реализует общие абстракции.

| Абстракция | Роль |
|---|---|
| `DbConnection` | соединение с БД |
| `DbCommand` | SQL-команда с параметрами |
| `DbDataReader` | потоковое чтение строк вперёд |
| `DbTransaction` | транзакция |
| `DbDataSource` (Npgsql `NpgsqlDataSource`) | фабрика соединений с пулом |

```csharp
var dataSource = NpgsqlDataSource.Create(connectionString);   // singleton на приложение
builder.Services.AddNpgsqlDataSource(connectionString);

await using var conn = await dataSource.OpenConnectionAsync(ct);
await using var cmd = new NpgsqlCommand("select id, name from users where id = $1", conn)
{
    Parameters = { new() { Value = id } }
};
await using var reader = await cmd.ExecuteReaderAsync(ct);
while (await reader.ReadAsync(ct))
    users.Add(new User(reader.GetGuid(0), reader.GetString(1)));
```

### Пул соединений

Открытие физического соединения дорого (TCP, TLS, аутентификация). `Open()` берёт соединение из пула, `Dispose()` (`Close()`) возвращает его обратно — физически оно не закрывается. Размер пула настраивается в строке подключения: `Maximum Pool Size=100`.

## Нюансы и подводные камни

- Не закрыл соединение — оно не вернулось в пул: «timeout waiting for a connection from the pool». Всегда `using`/`await using`.
- Держите соединение как можно меньше: открыл — выполнил — закрыл.
- Максимальный размер пула × число инстансов не должен превышать `max_connections` сервера PostgreSQL (используйте PgBouncer).
- `Read` и `ExecuteReader` держат соединение, пока reader открыт: не вызывайте второй запрос на том же соединении без MARS/multiplexing.
- Для больших выборок используйте `CommandBehavior.SequentialAccess` и потоковое чтение.

## Практика

1. Воспроизведите исчерпание пула, «забыв» закрыть соединение.
2. Настройте `NpgsqlDataSource` в DI и прочитайте данные через reader.
3. Сравните время запроса с пулом и `Pooling=false`.

## Вопросы с ответами

> [!question]- Что происходит при conn.Close() при включённом пуле?
> Соединение возвращается в пул и остаётся открытым на стороне БД, сбрасывается его состояние.

> [!question]- Почему возникает pool exhaustion?
> Соединения не освобождаются (утечка), запросы слишком долгие, либо пул мал для нагрузки.

> [!question]- Зачем PgBouncer при пуле в приложении?
> Ограничивает суммарное число соединений на сервере БД от многих инстансов приложения.

## Связанные темы

- [[N:3ea3310486798158868ffb2e607fee11]]
- [[N:3ea33104867981008e07e7e6edb5cbc2]]
