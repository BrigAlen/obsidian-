---
type: topic
domain: db
stage: 3
section: "3.1"
order: 6
status: todo
level: middle
notion_id: 3ea3310486798115b9c2c7343b02da24
tags: [domain/db, stage/3, level/middle, topic/clickhouse, topic/insert, topic/batch, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Вставка данных: батчи, async insert, почему нельзя по одной строке

↑ [[DB 3.1 ClickHouse|3.1 ClickHouse]] · ← [[DB 3.1.5 Типы данных и LowCardinality, Nullable, Array, Map|Предыдущая]] · → [[DB 3.1.7 Материализованные представления и проекции|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Самая частая ошибка новичков: вставка построчно. Нужно знать причины и решения.

## Почему нельзя по одной строке

Каждый `INSERT` создаёт **отдельный парт** на диске. Тысячи мелких вставок в секунду → тысячи партов → фоновые слияния не успевают → ошибка **`Too many parts`**, деградация чтения (нужно открывать много файлов), нагрузка на Keeper при репликации.

Правило: **вставляйте большими пачками** — минимум тысячи строк, лучше **10–100 тыс. и более** за вставку, не чаще **1 раза в секунду** на таблицу (ориентир).

## Способы

**Батчи на стороне клиента**

```sql
INSERT INTO events FORMAT JSONEachRow
{"event_time":"2026-09-30 12:00:00","user_id":1,"event_type":"click"}
{"event_time":"2026-09-30 12:00:01","user_id":2,"event_type":"view"}
```

Форматы: `Native` (самый быстрый), `RowBinary`, `CSV`, `JSONEachRow`, `Parquet`, `ArrowStream`. Клиентские библиотеки: ClickHouse.Client (.NET), clickhouse-go, clickhouse-connect (Python).

**Асинхронные вставки (async_insert)**

Сервер сам накапливает мелкие вставки в буфер и записывает одним пактом:

```sql
SET async_insert = 1, wait_for_async_insert = 1;
INSERT INTO events VALUES (...);
```

Настройки: `async_insert_max_data_size`, `async_insert_busy_timeout_ms`. `wait_for_async_insert = 1` — клиент получает подтверждение после записи (надёжнее), `0` — быстрее, но при сбое возможна потеря.

**Промежуточные буферы и очереди**

- Kafka Engine / Kafka Connect / Vector / Fluent Bit / Redpanda Connect собирают батчи;
- `Buffer`-таблица (устаревающий подход);
- буферизация на стороне приложения (пакет по размеру или времени).

## Идемпотентность и повторы

Для реплицируемых таблиц ClickHouse **дедуплицирует повторную вставку того же блока** (`insert_deduplicate`, окно последних блоков `replicated_deduplication_window`). Повтор вставки идентичных данных и порядка безопасен. Для надёжной доставки используйте одинаковые батчи при повторах (`insert_deduplication_token`).

## Эффективность

- сортировка данных батча по ключу не обязательна, но упрощает;
- вставка в **несколько партиций** одним батчем создаёт по парту на партицию: ограничивайте (`max_partitions_per_insert_block`);
- используйте `Native`/сжатие, параллельные вставки в разные шарды/реплики;
- массовая загрузка: `INSERT SELECT`, `clickhouse-local`, `s3()` табличная функция.

```sql
INSERT INTO events SELECT * FROM s3('https://bucket/data/*.parquet', 'Parquet');
```

## Мониторинг

```sql
SELECT table, count() AS parts, sum(rows) FROM system.parts WHERE active GROUP BY table;
SELECT * FROM system.part_log ORDER BY event_time DESC LIMIT 10;
```

Настройки: `parts_to_delay_insert`, `parts_to_throw_insert`.

## Вопросы с ответами

> [!question]- Почему вставка по одной строке убивает ClickHouse?
> Каждая вставка создаёт парт; слишком много партов приводит к ошибке Too many parts, нагрузке на слияния и медленным запросам. Нужны крупные батчи или async insert.

> [!question]- Что такое async_insert?
> Режим, при котором сервер собирает мелкие вставки в память и записывает их одним партом. Клиент может ждать подтверждения записи (`wait_for_async_insert = 1`).

> [!question]- Безопасно ли повторять вставку?
> Для реплицируемых таблиц одинаковый блок дедуплицируется; для остальных нужны идемпотентные ключи и ReplacingMergeTree.
