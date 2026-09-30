---
type: topic
domain: db
stage: 5
section: "5.1"
order: 4
status: todo
level: middle
notion_id: 3ea331048679811f9c79f014a3706f07
tags: [domain/db, stage/5, level/middle, topic/ef-core, topic/migrations, topic/dotnet, topic/cicd, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# Миграции EF Core в проде: bundles, скрипты, кто и когда применяет

↑ [[DB 5.1 Миграции — EF Core, Flyway, goose|5.1 Миграции: EF Core, Flyway, goose]] · ← [[DB 5.1.3 goose для ClickHouse|Предыдущая]] · → [[DB 5.1.5 Zero-downtime миграции — expand and contract, большие таблицы, индексы CONCURRENTLY|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Для .NET-разработчика ключевой вопрос: как безопасно доставлять EF-миграции в продакшн, а не через `Database.Migrate()` на старте.

## Создание миграций

```sh
dotnet tool install --global dotnet-ef
dotnet ef migrations add AddOrderStatus -p src/Infrastructure -s src/Api
dotnet ef migrations list
dotnet ef migrations remove            # удалить последнюю, если не применена
dotnet ef database update              # только локально!
```

Миграция — класс с `Up()` и `Down()` + снимок модели `ModelSnapshot`. История в таблице `__EFMigrationsHistory`.

**Проверяйте сгенерированное**: переименования EF иногда распознаёт как `DropColumn` + `AddColumn` (потеря данных); правьте вручную `RenameColumn`. Добавляйте SQL для бэкфилла: `migrationBuilder.Sql(...)`.

## Способы применения в проде

| Способ | Описание | Оценка |
|---|---|---|
| `context.Database.Migrate()` при старте | применяет миграции в коде приложения | **не рекомендуется** на проде: гонки между инстансами, права DDL у приложения, медленный старт, откаты при сбое |
| **SQL-скрипт** | `dotnet ef migrations script --idempotent -o migrate.sql` | проверяемый артефакт, применяется любым инструментом/DBA |
| **Migration bundle** | `dotnet ef migrations bundle` создаёт самодостаточный исполняемый файл | удобно для CI/CD и контейнеров |
| Отдельное консольное приложение | свой `Migrator` проект | гибкость, бэкфилл в коде |
| Внешний инструмент (Flyway/DbUp) | скрипты из EF | единый процесс с другими БД |

### SQL-скрипт

```sh
# все миграции, идемпотентно (проверяет __EFMigrationsHistory)
dotnet ef migrations script --idempotent -p src/Infrastructure -s src/Api -o artifacts/migrate.sql

# от миграции A до B
dotnet ef migrations script AddOrders AddOrderStatus -o artifacts/delta.sql
```

Скрипт проходит **ревью** (блокировки, скорость, `CREATE INDEX CONCURRENTLY`) и применяется `psql`.

### Migration bundle

```sh
dotnet ef migrations bundle --self-contained -r linux-x64 -p src/Infrastructure -s src/Api -o artifacts/efbundle

# применение
./efbundle --connection "Host=postgres;Database=app;Username=migrator;Password=$DB_PASSWORD"
```

Dockerfile для шага миграций:

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY . .
RUN dotnet tool install --global dotnet-ef && export PATH="$PATH:/root/.dotnet/tools" \
 && dotnet ef migrations bundle --self-contained -r linux-x64 -p src/Infrastructure -s src/Api -o /efbundle

FROM mcr.microsoft.com/dotnet/runtime-deps:9.0
COPY --from=build /efbundle /efbundle
ENTRYPOINT ["/efbundle"]
```

## Кто и когда применяет

```text
CI: build → test → собрать bundle/скрипт (артефакт)
CD: [1] бэкап/точка восстановления → [2] job миграций (migrator) → [3] выкатка приложения → [4] smoke-тесты
```

- в Kubernetes: Job или Helm `pre-upgrade` hook, либо init-контейнер с `initContainers` (ограничьте до одного запуска);
- **отдельный пользователь БД** для миграций (права DDL), приложение — с минимальными (DML);
- **обратная совместимость**: схема после миграции должна работать со **старой** версией приложения (rolling update);
- миграция применяется **до** кода, который её требует; удаление колонок — **после** выкатки кода, который её не использует.

## Проблемы и советы

- **Параллельные запуски**: EF (с .NET 9) использует блокировку на уровне БД (`__EFMigrationsLock` / advisory), но не полагайтесь: запускайте ровно один процесс;
- **Долгие миграции**: большие таблицы, `ALTER` с перезаписью — блокировки; см. zero-downtime;
- **`Down()`**: используйте осознанно; на проде предпочтителен roll-forward;
- **Конфликты веток**: две миграции от одного снимка → конфликт `ModelSnapshot`; решается пересозданием одной миграции после merge;
- **Seed-данные**: `HasData` попадает в миграции (изменения данных при каждом изменении), для справочников лучше отдельные скрипты/миграции данных;
- **Транзакции**: EF оборачивает каждую миграцию в транзакцию, если провайдер поддерживает; `suppressTransaction: true` для `CREATE INDEX CONCURRENTLY`:

```csharp
migrationBuilder.Sql("CREATE INDEX CONCURRENTLY idx_orders_status ON orders (status);", suppressTransaction: true);
```

- **Проверка дрейфа**: сравнение схемы прода с моделью (`dotnet ef migrations has-pending-model-changes` в CI — падает, если забыли создать миграцию).

## Тестирование

- интеграционные тесты на Testcontainers: поднять PostgreSQL, применить миграции, прогнать сценарии;
- проверка, что модель и миграции синхронны;
- прогон на копии продовых данных для оценки времени.

## Вопросы с ответами

> [!question]- Почему Database.Migrate() при старте — плохая практика на проде?
> Несколько инстансов запускаются одновременно (гонки), у приложения должны быть права на DDL, миграция замедляет или ломает старт, неудача приводит к падению сервиса, нет контроля и ревью.

> [!question]- Что такое migration bundle?
> Самодостаточный исполняемый файл, применяющий миграции EF к БД по строке подключения; удобно запускать как шаг пайплайна без SDK на целевой машине.

> [!question]- Зачем флаг --idempotent у скрипта?
> Скрипт проверяет `__EFMigrationsHistory` и применяет только отсутствующие миграции, поэтому его можно безопасно запускать на БД в любом состоянии.
