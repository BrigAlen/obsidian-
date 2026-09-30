---
type: topic
domain: db
stage: 1
section: "1.1"
order: 1
status: todo
level: junior
notion_id: 3ea331048679810488e7f7daf910f836
tags: [domain/db, stage/1, level/junior, topic/sql, topic/relational, topic/constraints, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Реляционная модель: таблицы, ключи, связи, ограничения

↑ [[DB 1.1 Реляционная модель и SQL|1.1 Реляционная модель и SQL]] · → [[DB 1.1.2 Нормализация и денормализация|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Базовый вопрос для любого backend-разработчика: чем отличаются виды ключей и какие ограничения защищают данные.

## Основные понятия

- **Отношение (таблица)**: набор строк одного типа; **строка (кортеж)** — запись; **столбец (атрибут)** — поле с типом.
- **Схема**: описание таблиц, типов, ключей и связей.
- В теории строки не упорядочены и не повторяются; в SQL порядок задаёт только `ORDER BY`.

## Ключи

| Ключ | Что это |
|---|---|
| **Первичный (PRIMARY KEY)** | уникально идентифицирует строку, не NULL; в таблице один |
| **Потенциальный (candidate)** | любой минимальный набор столбцов, однозначно определяющий строку |
| **Уникальный (UNIQUE)** | значения не повторяются, допускает NULL (в PostgreSQL несколько NULL) |
| **Внешний (FOREIGN KEY)** | ссылается на ключ другой таблицы, поддерживает ссылочную целостность |
| **Составной** | ключ из нескольких столбцов |
| **Естественный** | из предметной области (ИНН, email) |
| **Суррогатный** | искусственный (`bigint identity`, UUID) |

## Связи

- **один-к-одному**: `users` и `user_profiles` (внешний ключ с `UNIQUE`);
- **один-ко-многим**: `customers` → `orders` (внешний ключ на стороне «многих»);
- **многие-ко-многим**: через таблицу связи с составным ключом.

```sql
CREATE TABLE customers (
  id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email      text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE orders (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id bigint NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
  total       numeric(12,2) NOT NULL CHECK (total >= 0),
  status      text NOT NULL DEFAULT 'new' CHECK (status IN ('new','paid','shipped','cancelled'))
);

CREATE TABLE product_tags (            -- многие-ко-многим
  product_id bigint REFERENCES products(id) ON DELETE CASCADE,
  tag_id     bigint REFERENCES tags(id)     ON DELETE CASCADE,
  PRIMARY KEY (product_id, tag_id)
);
```

## Ограничения целостности

| Ограничение | Назначение |
|---|---|
| `NOT NULL` | значение обязательно |
| `UNIQUE` | уникальность |
| `CHECK` | произвольное условие на строку |
| `PRIMARY KEY` | уникальность + NOT NULL |
| `FOREIGN KEY` | ссылочная целостность |
| `EXCLUDE` (PostgreSQL) | например, непересекающиеся диапазоны броней |
| `DEFAULT` | значение по умолчанию |

## Действия внешнего ключа

`ON DELETE` / `ON UPDATE`: `RESTRICT` / `NO ACTION` (запретить), `CASCADE` (каскадно), `SET NULL`, `SET DEFAULT`. Для критичных данных предпочитайте `RESTRICT`, каскады применяйте осознанно.

## Нюансы

- **индексы на FK не создаются автоматически** в PostgreSQL: добавляйте вручную, иначе `JOIN` и удаления родителя медленные;
- ограничения — последняя линия защиты: не полагайтесь только на валидацию в приложении;
- `DEFERRABLE INITIALLY DEFERRED` откладывает проверку до конца транзакции (циклические ссылки).

## Вопросы с ответами

> [!question]- Чем PRIMARY KEY отличается от UNIQUE?
> Первичный ключ один на таблицу и не допускает NULL, уникальных ограничений может быть много, и они допускают NULL.

> [!question]- Зачем нужен внешний ключ, если приложение всё проверяет?
> Ограничение действует для всех клиентов и при гонках; приложение можно обойти или оно может содержать баг. БД гарантирует целостность.

> [!question]- Как реализовать связь многие-ко-многим?
> Отдельная таблица связи с внешними ключами на обе стороны и составным первичным ключом.
