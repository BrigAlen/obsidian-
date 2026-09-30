---
type: topic
domain: db
stage: 5
section: "5.1"
order: 2
status: todo
level: middle
notion_id: 3ea331048679816389cede7573b5e9c3
tags: [domain/db, stage/5, level/middle, topic/flyway, topic/migrations, topic/docker, priority/should]
reviewed:
next_review:
priority: should
time: 6
---

# Flyway: версионные и repeatable миграции, запуск в Docker

↑ [[DB 5.1 Миграции — EF Core, Flyway, goose|5.1 Миграции: EF Core, Flyway, goose]] · ← [[DB 5.1.1 Зачем версионировать схему БД — подходы state-based и migration-based|Предыдущая]] · → [[DB 5.1.3 goose для ClickHouse|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Flyway — самый простой и популярный инструмент SQL-миграций; часто встречается в Java/Kotlin и в контейнерных пайплайнах любого стека.

## Принцип

Flyway применяет SQL-файлы в порядке версий и хранит историю в таблице `flyway_schema_history` (версия, описание, checksum, время, успех).

## Типы миграций

| Тип | Имя файла | Поведение |
|---|---|---|
| **Versioned** | `V1__create_tables.sql`, `V2.1__add_index.sql` | выполняется **один раз**, в порядке версий |
| **Repeatable** | `R__views.sql` | выполняется **заново при изменении checksum** (после всех versioned); для представлений, функций, процедур |
| **Undo** | `U2__...` | откат (платная версия) |
| **Baseline** | `B5__...` | для существующей БД |
| **Callbacks** | `beforeMigrate.sql`, `afterMigrate.sql` | хуки |

Формат имени: `{префикс}{версия}__{описание}.sql` (**двойное** подчёркивание).

```sql
-- V3__orders_status.sql
ALTER TABLE orders ADD COLUMN status text NOT NULL DEFAULT 'new';
CREATE INDEX idx_orders_status ON orders (status);
```

```sql
-- R__v_active_customers.sql  (пересоздаётся при изменении)
CREATE OR REPLACE VIEW v_active_customers AS
SELECT id, email FROM customers WHERE deleted_at IS NULL;
```

## Запуск в Docker

```sh
docker run --rm --network app \
  -v "$PWD/db/migrations:/flyway/sql:ro" \
  flyway/flyway:11 \
  -url=jdbc:postgresql://postgres:5432/app \
  -user=app_migrator -password="$DB_PASSWORD" \
  -connectRetries=30 \
  migrate
```

В `docker-compose`:

```yaml
services:
  postgres:
    image: postgres:17
    healthcheck: { test: ["CMD-SHELL", "pg_isready -U app"], interval: 5s, retries: 10 }

  migrate:
    image: flyway/flyway:11
    command: -url=jdbc:postgresql://postgres:5432/app -user=app -password=${DB_PASSWORD} -connectRetries=30 migrate
    volumes: [ "./db/migrations:/flyway/sql:ro" ]
    depends_on:
      postgres: { condition: service_healthy }

  api:
    build: ./src/Api
    depends_on:
      migrate: { condition: service_completed_successfully }
```

В Kubernetes: **init-контейнер** или Job (Helm pre-upgrade hook) до запуска новых подов; следите, чтобы выполнялась ровно одна миграция.

## Основные команды

| Команда | Что делает |
|---|---|
| `migrate` | применить ожидающие миграции |
| `info` | статус: применённые, ожидающие, ошибочные |
| `validate` | проверить checksum и наличие файлов |
| `baseline` | пометить текущее состояние БД как версию (для существующих БД) |
| `repair` | починить таблицу истории (после сбоя) |
| `clean` | **удалить все объекты** (запрещать на проде: `cleanDisabled=true`) |

## Конфигурация

```toml
[flyway]
url = "jdbc:postgresql://localhost:5432/app"
locations = ["filesystem:db/migrations"]
validateMigrationNaming = true
outOfOrder = false                # false по умолчанию
baselineOnMigrate = false
cleanDisabled = true
placeholders.schema = "public"    # ${schema} в SQL
```

## Практики

- версия по времени (`V20260930_1200__...`) уменьшает конфликты в ветках, либо последовательные номера при строгом порядке;
- **checksum**: изменение применённого файла даёт ошибку валидации (защита);
- `outOfOrder` — применить «опоздавшую» версию меньше текущей (осторожно);
- отдельные пользователь `migrator` (DDL) и `app` (DML);
- PostgreSQL: Flyway оборачивает миграцию в транзакцию, для `CREATE INDEX CONCURRENTLY` используйте `-- flyway:executeInTransaction=false` (конфиг в файле `.conf` рядом или `executeInTransaction=false`);
- **advisory lock**: Flyway блокирует БД на время миграции, параллельные запуски безопасны;
- тестирование миграций на чистой БД в CI (`migrate` → тесты) и на «грязной» копии;
- для .NET есть обёртки (`FluentMigrator`, `DbUp`, `Evolve`), но CLI/Docker Flyway одинаково работает с любым стеком.

## Flyway против Liquibase

| | Flyway | Liquibase |
|---|---|---|
| Формат | SQL (и Java) | XML/YAML/JSON/SQL changelog |
| Кривая обучения | низкая | выше |
| Откат | платная Undo | rollback-блоки, богаче |
| Независимость от СУБД | меньше | выше (абстракция) |
| Контроль | `checksum` | `changeset` с id/author |

## Вопросы с ответами

> [!question]- Чем versioned отличается от repeatable миграции?
> Versioned выполняется один раз в порядке версий, repeatable — каждый раз при изменении содержимого (после versioned); подходит для представлений и функций.

> [!question]- Что произойдёт, если изменить уже применённую миграцию?
> `validate` обнаружит несовпадение checksum, миграция остановится с ошибкой. Исправление — новая миграция (или `repair`, если изменение осознанно и безопасно).

> [!question]- Как запустить миграции до старта приложения в docker-compose?
> Отдельный сервис `migrate` с зависимостью от здоровья БД и `depends_on: service_completed_successfully` для приложения.
