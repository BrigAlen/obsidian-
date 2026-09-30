---
type: topic
domain: backend
stage: 3
section: "3.6"
order: 3
status: todo
level: middle
notion_id: 3ea331048679810e9b74c450d13d065b
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/testing, topic/docker, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Testcontainers: настоящие БД и брокеры в тестах

↑ [[BE 3.6 Тестирование ASP.NET Core|3.6 Тестирование ASP.NET Core]] · ← [[BE 3.6.2 Интеграционные тесты — WebApplicationFactory|Предыдущая]] · → [[BE 3.6.4 Тестирование авторизации и middleware|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




























> [!info] Зачем это на собесе
> Современный стандарт интеграционных тестов: реальные PostgreSQL/Kafka в Docker вместо in-memory заглушек.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Testcontainers поднимает Docker-контейнеры на время тестов.

```csharp
public class DbFixture : IAsyncLifetime
{
    private readonly PostgreSqlContainer _pg = new PostgreSqlBuilder().WithImage("postgres:16").Build();
    public string ConnectionString => _pg.GetConnectionString();

    public Task InitializeAsync() => _pg.StartAsync();
    public Task DisposeAsync() => _pg.DisposeAsync().AsTask();
}

public class ApiFactory(DbFixture db) : WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder b) =>
        b.UseSetting("ConnectionStrings:Default", db.ConnectionString);
}
```

| Подход | Плюсы | Минусы |
|---|---|---|
| EF InMemory | быстро | другое поведение, нет SQL/транзакций/ограничений |
| SQLite in-memory | лучше | диалект отличается от прод |
| Testcontainers | реальное поведение | нужен Docker, дольше старт |

Готовые модули: PostgreSql, MsSql, MongoDb, Redis, Kafka, RabbitMq, MinIO, Keycloak.

## Нюансы и подводные камни

- Один контейнер на набор тестов (collection fixture), а не на тест.
- В CI нужен Docker (GitHub Actions поддерживает из коробки).
- Применяйте миграции при старте фикстуры.
- Порты случайные: берите строку подключения из контейнера.
- Ryuk удаляет контейнеры даже при падении; не отключайте без необходимости.

## Практика

1. Замените EF InMemory на PostgreSQL в Testcontainers.
2. Добавьте Kafka-контейнер и протестируйте публикацию/потребление.
3. Проверьте время прогона и оптимизируйте переиспользованием контейнера.

## Вопросы с ответами

> [!question]- Почему Testcontainers лучше InMemory?
> Реальная БД воспроизводит SQL, ограничения, транзакции и миграции.

> [!question]- Как ускорить тесты с контейнерами?
> Один контейнер на коллекцию, очистка данных вместо пересоздания, параллельность по схемам.

## Связанные темы

- [[N:3ea3310486798124a799c04cc2451379]]
- [[N:3ea3310486798199a2e6f67582af01e4]]
