---
type: topic
domain: db
stage: 2
section: "2.1"
order: 8
status: todo
level: middle
notion_id: 3ea331048679812ab7b7e22f883e6cb0
tags: [domain/db, stage/2, level/middle, topic/postgresql, topic/jsonb, topic/full-text-search, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# JSONB, массивы, полнотекстовый поиск

↑ [[DB 2.1 PostgreSQL — индексы, транзакции, оптимизация|2.1 PostgreSQL: индексы, транзакции, оптимизация]] · ← [[DB 2.1.7 Блокировки — row, table, advisory, SELECT FOR UPDATE, deadlocks|Предыдущая]] · → [[DB 2.1.9 Партиционирование таблиц|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> PostgreSQL часто заменяет отдельную документную БД или поисковый движок для несложных задач.

## JSON и JSONB

| | `json` | `jsonb` |
|---|---|---|
| Хранение | текст как есть | бинарное, разобранное |
| Порядок ключей, пробелы | сохраняются | нет, дубликаты ключей убираются |
| Индексы | нет | да (GIN) |
| Скорость запросов | ниже | выше |

**Почти всегда используйте `jsonb`.**

```sql
CREATE TABLE events (id bigserial PRIMARY KEY, payload jsonb NOT NULL);

SELECT payload -> 'user' ->> 'name'            AS name,     -- -> объект, ->> текст
       payload #>> '{user,address,city}'       AS city,
       (payload ->> 'amount')::numeric         AS amount
FROM events
WHERE payload @> '{"type": "purchase"}'        -- содержит
  AND payload ? 'coupon'                        -- ключ существует
  AND payload -> 'tags' ? 'vip';

UPDATE events SET payload = jsonb_set(payload, '{status}', '"done"') WHERE id = 1;
UPDATE events SET payload = payload || '{"seen": true}'   -- слияние
                  , payload = payload - 'temp';           -- удаление ключа

SELECT jsonb_path_query(payload, '$.items[*] ? (@.price > 100)') FROM events;   -- JSONPath
```

## Индексы

```sql
CREATE INDEX idx_events_payload ON events USING gin (payload);                    -- @>, ?, ?|, ?&
CREATE INDEX idx_events_payload_path ON events USING gin (payload jsonb_path_ops); -- только @>, меньше и быстрее
CREATE INDEX idx_events_type ON events ((payload ->> 'type'));                    -- B-tree по выражению для равенства
```

## Когда JSONB, а когда столбцы

Используйте JSONB для полуструктурированных, редко фильтруемых атрибутов, интеграционных payload'ов, настроек. Не используйте, если поля стабильны и часто участвуют в `JOIN`, `WHERE`, ограничениях: столбцы дают типы, `CHECK`, внешние ключи, статистику. Гибрид: основные поля — столбцами, «хвост» — в `jsonb`.

Ограничения: обновление одного ключа переписывает весь документ (большие значения — TOAST), нет ссылочной целостности, планировщик хуже оценивает селективность.

## Массивы

```sql
CREATE TABLE posts (id bigserial PRIMARY KEY, tags text[] NOT NULL DEFAULT '{}');

SELECT * FROM posts WHERE tags @> ARRAY['sql'];       -- содержит
SELECT * FROM posts WHERE 'sql' = ANY(tags);
SELECT unnest(tags) AS tag, count(*) FROM posts GROUP BY 1;
UPDATE posts SET tags = array_append(tags, 'pg') WHERE id = 1;

CREATE INDEX idx_posts_tags ON posts USING gin (tags);
```

Массивы удобны для небольших списков; для связей с ссылочной целостностью — таблица связи.

## Полнотекстовый поиск

```sql
ALTER TABLE articles ADD COLUMN tsv tsvector
  GENERATED ALWAYS AS (to_tsvector('russian', coalesce(title,'') || ' ' || coalesce(body,''))) STORED;
CREATE INDEX idx_articles_tsv ON articles USING gin (tsv);

SELECT id, title, ts_rank(tsv, q) AS rank, ts_headline('russian', body, q) AS snippet
FROM articles, websearch_to_tsquery('russian', 'индексы "полнотекстовый поиск" -mysql') q
WHERE tsv @@ q
ORDER BY rank DESC LIMIT 20;
```

- `to_tsvector` — нормализованный вектор лексем (стемминг по словарю языка);
- `to_tsquery`, `plainto_tsquery`, `websearch_to_tsquery` — разбор запроса;
- веса `setweight(..., 'A')` для заголовка;
- нечёткий поиск и `LIKE '%x%'`: расширение `pg_trgm` + GIN (`similarity`, `%`);
- при сложных требованиях (фасеты, морфология, масштаб) — Elasticsearch/OpenSearch, Meilisearch.

## Вопросы с ответами

> [!question]- Чем jsonb отличается от json?
> jsonb хранится в разобранном бинарном виде, поддерживает индексы и быстрые операторы, но не сохраняет форматирование и порядок ключей.

> [!question]- Как ускорить поиск по полю внутри jsonb?
> GIN-индекс по всему документу для `@>`/`?` или B-tree по выражению `(payload ->> 'field')` для равенства и сортировки.

> [!question]- Когда хватит PostgreSQL для поиска?
> Для умеренных объёмов и простого ранжирования: tsvector + GIN + pg_trgm. Для сложной релевантности, фасетов и больших объёмов нужен специализированный движок.
