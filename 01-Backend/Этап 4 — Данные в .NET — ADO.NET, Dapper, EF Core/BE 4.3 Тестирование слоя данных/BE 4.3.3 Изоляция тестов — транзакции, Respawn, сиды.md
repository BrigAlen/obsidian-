---
type: topic
domain: backend
stage: 4
section: "4.3"
order: 3
status: todo
level: middle
notion_id: 3ea331048679815bb5afc471e7639ef7
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/testing, topic/data, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Изоляция тестов: транзакции, Respawn, сиды

↑ [[BE 4.3 Тестирование слоя данных|4.3 Тестирование слоя данных]] · ← [[BE 4.3.2 Testcontainers для PostgreSQL и ClickHouse|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->














> [!info] Зачем это на собесе
> Как сделать тесты независимыми и повторяемыми при общей БД.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Способ | Как | Плюсы | Минусы |
|---|---|---|---|
| Транзакция с откатом | каждый тест в транзакции, rollback в конце | очень быстро | не подходит для кода, сам управляющий транзакциями |
| Respawn | очистка данных (DELETE/TRUNCATE) перед тестом | универсально | чуть медленнее |
| БД на тест / схема на тест | полная изоляция | максимально надёжно | дорого |
| Пересоздание контейнера | чистое состояние | долго | только для редких тестов |

```csharp
public class OrdersTests(PgFixture fx) : IAsyncLifetime
{
    private Respawner _respawner = default!;
    public async Task InitializeAsync()
    {
        await using var conn = new NpgsqlConnection(fx.ConnectionString);
        await conn.OpenAsync();
        _respawner = await Respawner.CreateAsync(conn, new RespawnerOptions { DbAdapter = DbAdapter.Postgres, TablesToIgnore = ["__EFMigrationsHistory"] });
        await _respawner.ResetAsync(conn);
    }
    public Task DisposeAsync() => Task.CompletedTask;
}
```

### Сиды

- Справочники — часть миграций или отдельный seed; тестовые данные создавайте явно в тесте (builder-ы), а не полагайтесь на общий «мир».
- Каждый тест создаёт только нужные ему данные и уникальные значения (GUID), тогда параллельный запуск безопасен.

## Нюансы и подводные камни

- Общие данные между тестами — источник flaky.
- Порядок тестов не должен влиять на результат.
- Параллельные тесты на одной БД: изолируйте по схеме или отключайте параллелизм коллекции.
- Не забудьте исключить таблицу истории миграций при очистке.

## Практика

1. Подключите Respawn и убедитесь, что тесты не зависят друг от друга.
2. Сравните время: rollback, Respawn, пересоздание БД.
3. Напишите builder для сложного агрегата с разумными значениями по умолчанию.

## Вопросы с ответами

> [!question]- Как изолировать тесты при общей БД?
> Откат транзакции, Respawn-очистка либо отдельная БД/схема на тест.

> [!question]- Почему не полагаться на общий seed?
> Тесты становятся связаны и хрупки; данные нужно создавать явно в самом тесте.

## Связанные темы

- [[N:3ea33104867981bb9daceb1fff42831f]]
- [[N:3ea3310486798124a799c04cc2451379]]
