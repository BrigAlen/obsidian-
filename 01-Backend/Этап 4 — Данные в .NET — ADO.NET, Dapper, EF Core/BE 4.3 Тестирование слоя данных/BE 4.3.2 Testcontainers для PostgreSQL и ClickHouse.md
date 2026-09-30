---
type: topic
domain: backend
stage: 4
section: "4.3"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981bb9daceb1fff42831f
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/testing, topic/docker, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Testcontainers для PostgreSQL и ClickHouse

↑ [[BE 4.3 Тестирование слоя данных|4.3 Тестирование слоя данных]] · ← [[BE 4.3.1 InMemory и SQLite провайдеры — подводные камни|Предыдущая]] · → [[BE 4.3.3 Изоляция тестов — транзакции, Respawn, сиды|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Практическая реализация «тестов на настоящей БД» в CI.

## Объяснение

```csharp
public class PgFixture : IAsyncLifetime
{
    private readonly PostgreSqlContainer _pg = new PostgreSqlBuilder()
        .WithImage("postgres:16-alpine").WithDatabase("test").Build();

    public string ConnectionString => _pg.GetConnectionString();

    public async Task InitializeAsync()
    {
        await _pg.StartAsync();
        await using var db = CreateContext();
        await db.Database.MigrateAsync();   // реальные миграции проверяются тоже
    }

    public Task DisposeAsync() => _pg.DisposeAsync().AsTask();
    public AppDbContext CreateContext() => new(new DbContextOptionsBuilder<AppDbContext>().UseNpgsql(ConnectionString).Options);
}

[CollectionDefinition("db")] public class DbCollection : ICollectionFixture<PgFixture> { }
```

ClickHouse: `new ClickHouseBuilder().WithImage("clickhouse/clickhouse-server:24").Build()`, схема создаётся SQL-скриптом при старте.

## Нюансы и подводные камни

- Один контейнер на коллекцию; не запускайте контейнер на каждый тест.
- В CI нужен доступ к Docker-демону (GitHub Actions: доступен по умолчанию).
- Фиксируйте версию образа как в продакшене.
- Порты случайны: используйте `GetConnectionString()`.
- Кэшируйте образы в CI, чтобы не тратить время на pull.

## Практика

1. Поднимите PostgreSQL через Testcontainers и прогоните миграции.
2. Добавьте ClickHouse и протестируйте вставку батча.
3. Замерьте время старта и подберите стратегию переиспользования.

## Вопросы с ответами

> [!question]- Зачем прогонять миграции в тестах?
> Проверяется, что схема, создаваемая миграциями, совместима с моделью и запросами.

> [!question]- Как ускорить тесты с контейнерами?
> Один контейнер на коллекцию, очистка данных вместо пересоздания, кэш образов.

## Связанные темы

- [[N:3ea33104867981df8306e2ce8ba91fbb]]
- [[N:3ea331048679815bb5afc471e7639ef7]]
