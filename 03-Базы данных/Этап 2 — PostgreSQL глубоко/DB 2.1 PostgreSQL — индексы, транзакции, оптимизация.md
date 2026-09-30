---
type: section
domain: db
stage: 2
section: "2.1"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981f49e5eeba592c493ad
tags: [domain/db, stage/2, kind/section]
---

# 2.1 PostgreSQL: индексы, транзакции, оптимизация

↑ [[DB Этап 2 · PostgreSQL глубоко|Этап 2]]

Архитектура, индексы, EXPLAIN, ACID и изоляция, MVCC и VACUUM, блокировки, JSONB, партиционирование, оптимизация и PgBouncer, функции и представления.

## Темы
<!-- toc:start -->
**Итого:** 11 тем · ~39 мин · готово 0 из 11

<div class="bar"><span style="width:0%"></span></div>

| # | Тема | Приоритет | Чтение | Статус |
|---|---|---|---|---|
| 1 | [[DB 2.1.1 Архитектура PostgreSQL — процессы, страницы, WAL, shared buffers\|Архитектура PostgreSQL: процессы, страницы, WAL, shared buffers]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 2 | [[DB 2.1.2 Индексы — B-tree, Hash, GIN, GiST, BRIN, составные, частичные, covering\|Индексы: B-tree, Hash, GIN, GiST, BRIN, составные, частичные, covering]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 3 | [[DB 2.1.3 EXPLAIN и EXPLAIN ANALYZE — чтение плана, seq scan, index scan, joins\|EXPLAIN и EXPLAIN ANALYZE: чтение плана, seq scan, index scan, joins]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 4 | [[DB 2.1.4 Транзакции и ACID\|Транзакции и ACID]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 5 | [[DB 2.1.5 Уровни изоляции и аномалии — dirty read, non-repeatable, phantom, serialization\|Уровни изоляции и аномалии: dirty read, non-repeatable, phantom, serialization]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 6 | [[DB 2.1.6 MVCC, VACUUM, bloat\|MVCC, VACUUM, bloat]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 7 | [[DB 2.1.7 Блокировки — row, table, advisory, SELECT FOR UPDATE, deadlocks\|Блокировки: row, table, advisory, SELECT FOR UPDATE, deadlocks]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 8 | [[DB 2.1.8 JSONB, массивы, полнотекстовый поиск\|JSONB, массивы, полнотекстовый поиск]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 9 | [[DB 2.1.9 Партиционирование таблиц\|Партиционирование таблиц]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 10 | [[DB 2.1.10 Оптимизация запросов и пул соединений (PgBouncer)\|Оптимизация запросов и пул соединений (PgBouncer)]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 11 | [[DB 2.1.11 Функции, триггеры, представления, materialized views\|Функции, триггеры, представления, materialized views]] | <span class="badge must">Обязательно</span> | 5 мин | <span class="badge todo">Не начато</span> |
<!-- toc:end -->

## Чек-лист раздела
- [ ] Прочитал все темы
- [ ] Могу объяснить каждую тему за 2 минуты вслух
