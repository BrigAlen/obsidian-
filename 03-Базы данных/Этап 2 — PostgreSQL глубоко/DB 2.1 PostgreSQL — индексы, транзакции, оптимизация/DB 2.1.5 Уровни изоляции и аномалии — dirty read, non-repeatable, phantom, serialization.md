---
type: topic
domain: db
stage: 2
section: "2.1"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981cf94d1da61a5300846
tags: [domain/db, stage/2, level/middle, topic/postgresql, topic/isolation, topic/anomalies, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Уровни изоляции и аномалии: dirty read, non-repeatable, phantom, serialization

↑ [[DB 2.1 PostgreSQL — индексы, транзакции, оптимизация|2.1 PostgreSQL: индексы, транзакции, оптимизация]] · ← [[DB 2.1.4 Транзакции и ACID|Предыдущая]] · → [[DB 2.1.6 MVCC, VACUUM, bloat|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Один из самых частых вопросов: аномалии и что даёт каждый уровень в PostgreSQL.

## Аномалии

| Аномалия | Описание |
|---|---|
| **Dirty read** | чтение незакоммиченных данных другой транзакции |
| **Non-repeatable read** | повторное чтение той же строки даёт другое значение (её изменила и закоммитила другая транзакция) |
| **Phantom read** | повторный запрос по условию возвращает другой набор строк |
| **Lost update** | две транзакции читают, затем обе пишут: одно обновление теряется |
| **Write skew** | обе транзакции читают пересекающиеся данные и пишут в разные строки, нарушая общее условие |
| **Serialization anomaly** | результат невозможен ни при каком последовательном порядке |

## Уровни по стандарту SQL

| Уровень | Dirty | Non-repeatable | Phantom |
|---|---|---|---|
| Read Uncommitted | возможно | возможно | возможно |
| Read Committed | нет | возможно | возможно |
| Repeatable Read | нет | нет | возможно |
| Serializable | нет | нет | нет |

## PostgreSQL

| Уровень | Особенности |
|---|---|
| **Read Committed** (по умолчанию) | каждый оператор видит снимок на момент **своего начала**; Read Uncommitted работает как Read Committed |
| **Repeatable Read** | снимок фиксируется на первом операторе транзакции; (snapshot isolation) фантомы **не возникают**, но возможен write skew; при конфликте обновления — ошибка `could not serialize access` |
| **Serializable** | SSI (Serializable Snapshot Isolation): отслеживает опасные зависимости, при риске аномалии — ошибка `40001`, транзакцию нужно **повторить** |

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- или
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

## Пример: lost update и как избежать

```sql
-- небезопасно (read-modify-write в приложении)
SELECT balance FROM accounts WHERE id = 1;     -- 100
-- приложение считает 100 - 30 = 70
UPDATE accounts SET balance = 70 WHERE id = 1; -- перезаписывает чужое изменение

-- решения
UPDATE accounts SET balance = balance - 30 WHERE id = 1;          -- атомарно на сервере
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;            -- пессимистическая блокировка
UPDATE accounts SET balance = ?, version = version + 1
 WHERE id = 1 AND version = ?;                                    -- оптимистичная (проверка version)
```

## Write skew (пример)

Правило: в смене должен остаться хотя бы один врач. Два врача одновременно проверяют «сейчас двое дежурных», оба уходят: осталось ноль. Repeatable Read не спасёт; помогает **Serializable** или блокировка (`SELECT ... FOR UPDATE` по набору, advisory lock).

## Выбор уровня

- **Read Committed** — большинство приложений, с явными блокировками и атомарными обновлениями там, где нужно;
- **Repeatable Read** — согласованные отчёты (снимок на одну транзакцию), готовность к retry;
- **Serializable** — сложные инварианты; обязательно retry-логика; чуть выше накладные расходы.

## Вопросы с ответами

> [!question]- Возможен ли dirty read в PostgreSQL?
> Нет: даже на уровне Read Uncommitted PostgreSQL ведёт себя как Read Committed благодаря MVCC.

> [!question]- Чем Repeatable Read в PostgreSQL отличается от стандартного?
> Реализован как snapshot isolation: фантомов нет, но возможен write skew. При конфликтующих обновлениях возвращается ошибка сериализации.

> [!question]- Что делать при ошибке 40001?
> Повторить всю транзакцию (с ограничением числа попыток и задержкой); это нормальный режим работы на Serializable и Repeatable Read.
