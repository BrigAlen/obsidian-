---
type: topic
domain: db
stage: 7
order: 1
notion_id: 101f69fc0e25471ab70b02c4159c41d5
status: todo
level: middle+
tags: [domain/db, stage/7, level/middle+, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 6
---

# Роли, GRANT-REVOKE и Row-Level Security

↑ [[DB Этап 7 · Эксплуатация и безопасность БД|Этап 7 · Эксплуатация и безопасность БД]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Безопасность БД начинается с прав: принцип минимальных привилегий и разделение ролей миграций, приложения и аналитиков.

## Модель ролей PostgreSQL

В PostgreSQL нет разделения «пользователь» и «группа»: есть **роли** (`ROLE`). Роль с атрибутом `LOGIN` может подключаться (пользователь), без него — группа прав.

```sql
CREATE ROLE app_readonly NOLOGIN;                 -- группа прав
CREATE ROLE app_readwrite NOLOGIN;
CREATE ROLE app_migrator LOGIN PASSWORD '...' ;   -- владелец схемы, права DDL
CREATE ROLE app_service LOGIN PASSWORD '...' CONNECTION LIMIT 50;

GRANT app_readwrite TO app_service;               -- членство в роли (наследование прав)
```

Атрибуты: `SUPERUSER` (обходит все проверки — не для приложений), `CREATEDB`, `CREATEROLE`, `REPLICATION`, `BYPASSRLS`, `INHERIT`, `CONNECTION LIMIT`, `VALID UNTIL`.

## GRANT и REVOKE

```sql
-- базовая настройка безопасного доступа
REVOKE ALL ON DATABASE app FROM PUBLIC;           -- роль PUBLIC = все; по умолчанию может подключаться
REVOKE CREATE ON SCHEMA public FROM PUBLIC;       -- в PostgreSQL 15+ уже так по умолчанию

GRANT CONNECT ON DATABASE app TO app_readonly, app_readwrite;
GRANT USAGE ON SCHEMA app TO app_readonly, app_readwrite;

GRANT SELECT ON ALL TABLES IN SCHEMA app TO app_readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app TO app_readwrite;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA app TO app_readwrite;
GRANT EXECUTE ON FUNCTION app.order_total(bigint) TO app_readwrite;

-- права на будущие объекты
ALTER DEFAULT PRIVILEGES FOR ROLE app_migrator IN SCHEMA app
  GRANT SELECT ON TABLES TO app_readonly;
ALTER DEFAULT PRIVILEGES FOR ROLE app_migrator IN SCHEMA app
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;

-- колонки
GRANT SELECT (id, email, created_at) ON app.users TO support_team;   -- без хэша пароля и телефона
REVOKE DELETE ON app.orders FROM app_readwrite;
```

Проверки: `\dp` (права на таблицы), `\du` (роли), `has_table_privilege('app_service', 'app.orders', 'INSERT')`, `information_schema.role_table_grants`.

## Схема ролей для приложения

| Роль | Права | Кто использует |
|---|---|---|
| `app_migrator` | владелец объектов, DDL | пайплайн миграций |
| `app_service` (члены `app_readwrite`) | DML, без DDL | бэкенд |
| `app_readonly` | `SELECT` | отчёты, BI, аналитики |
| `backup_user` | `pg_read_all_data`, `REPLICATION` | резервное копирование |
| `monitoring` | `pg_monitor` | postgres_exporter, Grafana |
| `dba_admin` | суперпользователь (по запросу) | люди, с аудитом |

Встроенные роли: `pg_read_all_data`, `pg_write_all_data`, `pg_monitor`, `pg_read_all_stats`, `pg_signal_backend`.

**Принцип минимальных привилегий**: приложение не владелец таблиц и не суперпользователь; одна БД/схема — отдельные учётные записи на сервис.

## Row-Level Security (RLS)

Политики, ограничивающие **видимые и изменяемые строки** для роли. Ключ для многоарендных (multi-tenant) систем.

```sql
ALTER TABLE app.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.orders FORCE ROW LEVEL SECURITY;      -- действует и на владельца таблицы

-- арендатор задаётся параметром сессии
CREATE POLICY tenant_isolation ON app.orders
  USING      (tenant_id = current_setting('app.tenant_id')::bigint)            -- какие строки видны (SELECT/UPDATE/DELETE)
  WITH CHECK (tenant_id = current_setting('app.tenant_id')::bigint);           -- какие строки можно вставить/изменить

-- в начале транзакции из приложения
BEGIN;
SELECT set_config('app.tenant_id', '42', true);      -- true = только в этой транзакции
SELECT * FROM app.orders;                            -- видны только заказы тенанта 42
COMMIT;
```

Политики по командам и ролям:

```sql
CREATE POLICY own_rows_read   ON docs FOR SELECT TO app_user USING (owner_id = current_user_id());
CREATE POLICY admin_all       ON docs FOR ALL    TO app_admin USING (true);
```

Нюансы RLS:

- суперпользователи и роли с `BYPASSRLS` **обходят** политики; владелец таблицы тоже, если нет `FORCE`;
- политики — это условия, добавляемые к запросу: **индексируйте** столбцы политики (`tenant_id`), иначе замедление;
- при пуле соединений в режиме transaction используйте `set_config(..., true)` внутри транзакции, не `SET` на сессию (утечка контекста между клиентами);
- избегайте сложных подзапросов в политиках (производительность);
- не полагайтесь на RLS как единственную защиту: проверки в приложении тоже нужны;
- `security_invoker` для представлений (PG15+), чтобы представление выполнялось с правами вызывающего, а не владельца.

## Безопасность функций

- `SECURITY DEFINER` исполняет функцию от имени владельца: обязательно фиксируйте `SET search_path = pg_catalog, app`, иначе подмена объектов;
- отзывайте `EXECUTE` у `PUBLIC` для чувствительных функций.

## Аутентификация

- `pg_hba.conf`: кто, откуда, к какой БД и каким методом: предпочитайте **`scram-sha-256`**, а не `md5`/`trust`; `hostssl` для удалённых;
- внешние: LDAP, Kerberos/GSSAPI, сертификаты, OIDC (PostgreSQL 18), IAM-аутентификация в облаке;
- ограничение сетей, отдельные учётные записи на сервис, ротация паролей.

```text
# pg_hba.conf
hostssl  app  app_service  10.0.0.0/16  scram-sha-256
hostssl  all  all          0.0.0.0/0     reject
```

## Аудит

- `log_connections`, `log_disconnections`, `log_statement = 'ddl'`;
- расширение **pgaudit** (аудит операций по ролям и объектам);
- аудит изменений данных триггерами или CDC;
- журналы отправляются в централизованное хранилище.

## Вопросы с ответами

> [!question]- Почему приложению не дают права суперпользователя или владельца таблиц?
> При компрометации (SQL-инъекция, утечка пароля) атакующий получит минимальные возможности: нет DDL, нельзя создавать роли и читать чужие БД. Миграции выполняет отдельная роль.

> [!question]- Как работает Row-Level Security?
> Для таблицы включаются политики, задающие условия видимости (`USING`) и допустимости изменений (`WITH CHECK`) строк для ролей; планировщик добавляет эти условия к каждому запросу. Удобно для изоляции арендаторов.

> [!question]- Чем опасен SECURITY DEFINER?
> Функция выполняется с правами владельца; если не зафиксировать `search_path`, злоумышленник подменит объекты в своей схеме и повысит права.
