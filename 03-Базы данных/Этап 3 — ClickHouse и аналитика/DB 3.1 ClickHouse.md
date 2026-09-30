---
type: section
domain: db
stage: 3
section: "3.1"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981548429f1585cfdd2a1
tags: [domain/db, stage/3, kind/section]
---

# 3.1 ClickHouse

↑ [[DB Этап 3 · ClickHouse и аналитика|Этап 3]]

OLAP-хранилище: колоночная модель, архитектура MergeTree, вставка, представления, мутации, оптимизация запросов, интеграции, репликация и шардирование.

## Темы
<!-- toc:start -->
**Итого:** 11 тем · ~40 мин · готово 0 из 11

<div class="bar"><span style="width:0%"></span></div>

| # | Тема | Приоритет | Чтение | Статус |
|---|---|---|---|---|
| 1 | [[DB 3.1.1 OLTP и OLAP, строковое и колоночное хранение\|OLTP и OLAP, строковое и колоночное хранение]] | <span class="badge should">Желательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 2 | [[DB 3.1.2 Архитектура ClickHouse — парты, гранулы, sparse index, сжатие\|Архитектура ClickHouse: парты, гранулы, sparse index, сжатие]] | <span class="badge should">Желательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 3 | [[DB 3.1.3 Движок MergeTree — ORDER BY, PRIMARY KEY, PARTITION BY, TTL\|Движок MergeTree: ORDER BY, PRIMARY KEY, PARTITION BY, TTL]] | <span class="badge should">Желательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 4 | [[DB 3.1.4 Семейство MergeTree — Replacing, Summing, Aggregating, Collapsing\|Семейство MergeTree: Replacing, Summing, Aggregating, Collapsing]] | <span class="badge should">Желательно</span> | 5 мин | <span class="badge todo">Не начато</span> |
| 5 | [[DB 3.1.5 Типы данных и LowCardinality, Nullable, Array, Map\|Типы данных и LowCardinality, Nullable, Array, Map]] | <span class="badge should">Желательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 6 | [[DB 3.1.6 Вставка данных — батчи, async insert, почему нельзя по одной строке\|Вставка данных: батчи, async insert, почему нельзя по одной строке]] | <span class="badge should">Желательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 7 | [[DB 3.1.7 Материализованные представления и проекции\|Материализованные представления и проекции]] | <span class="badge should">Желательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 8 | [[DB 3.1.8 UPDATE и DELETE в ClickHouse — mutations, lightweight delete\|UPDATE и DELETE в ClickHouse: mutations, lightweight delete]] | <span class="badge should">Желательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 9 | [[DB 3.1.9 Запросы и оптимизация — агрегации, JOIN, FINAL, словари\|Запросы и оптимизация: агрегации, JOIN, FINAL, словари]] | <span class="badge should">Желательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 10 | [[DB 3.1.10 Интеграции — Kafka engine, телеметрия OTel в ClickHouse, Grafana\|Интеграции: Kafka engine, телеметрия OTel в ClickHouse, Grafana]] | <span class="badge should">Желательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 11 | [[DB 3.1.11 Репликация и шардирование — ReplicatedMergeTree, Distributed, Keeper\|Репликация и шардирование: ReplicatedMergeTree, Distributed, Keeper]] | <span class="badge should">Желательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
<!-- toc:end -->

## Чек-лист раздела
- [ ] Прочитал все темы
- [ ] Могу объяснить каждую тему за 2 минуты вслух
