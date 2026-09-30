---
type: topic
domain: db
stage: 3
section: "3.1"
order: 5
status: todo
level: middle
notion_id: 3ea3310486798177b771e54d43fee52f
tags: [domain/db, stage/3, level/middle, topic/clickhouse, topic/data-types, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Типы данных и LowCardinality, Nullable, Array, Map

↑ [[DB 3.1 ClickHouse|3.1 ClickHouse]] · ← [[DB 3.1.4 Семейство MergeTree — Replacing, Summing, Aggregating, Collapsing|Предыдущая]] · → [[DB 3.1.6 Вставка данных — батчи, async insert, почему нельзя по одной строке|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Правильные типы напрямую влияют на размер данных и скорость запросов.

## Числа и время

| Тип | Заметки |
|---|---|
| `UInt8/16/32/64`, `Int8..Int64`, `UInt128/256` | выбирайте минимально достаточный |
| `Float32/64` | приближённые, для метрик |
| `Decimal(P,S)` | деньги, точные значения |
| `Date`, `Date32` | дата (Date32 — расширенный диапазон) |
| `DateTime`, `DateTime64(3)` | секунды / точность до мс, мкс |
| `Bool` | булево |
| `UUID`, `IPv4`, `IPv6` | компактные типы |
| `Enum8/16` | набор значений, компактно |

Часовой пояс: `DateTime('Europe/Moscow')` хранит UTC, отображает в зоне.

## Строки

- `String` — произвольные байты, без ограничения длины;
- `FixedString(N)` — фиксированная длина (хэши, коды);
- **`LowCardinality(String)`** — словарное кодирование для столбцов с малым числом уникальных значений (до ~10⁴–10⁵): сильное сжатие и ускорение фильтров/группировок.

```sql
event_type LowCardinality(String)   -- 'click', 'view', 'purchase', ...
country    LowCardinality(FixedString(2))
```

Не применяйте к высококардинальным (id, URL): станет хуже.

## Nullable

`Nullable(T)` добавляет отдельный файл-маску NULL: **замедляет и увеличивает** данные. Рекомендация: избегать, использовать значения по умолчанию (`0`, пустая строка) или специальные значения; Nullable — только если NULL несёт смысл.

## Составные типы

```sql
tags    Array(String)                        -- массивы
attrs   Map(String, String)                  -- словарь ключ→значение
point   Tuple(Float64, Float64)
nested  Nested(name String, value Float64)   -- параллельные массивы
json    JSON                                 -- полуструктурированные данные (новый тип JSON)
```

Функции для массивов: `arrayJoin`, `has`, `arrayMap`, `arrayFilter`, `groupArray`, `arrayZip`, лямбды.

```sql
SELECT arrayJoin(tags) AS tag, count() FROM posts GROUP BY tag;
SELECT attrs['browser'] AS browser, count() FROM events GROUP BY browser;
```

`Map` хранит все ключи в одном столбце: чтение одного ключа читает весь Map. Если ключи известны и часто используются, выносите в отдельные столбцы или **материализованные столбцы**.

## Материализованные и алиасные столбцы

```sql
browser String MATERIALIZED attrs['browser'],     -- вычисляется при вставке и хранится
day     Date   ALIAS toDate(ts)                   -- вычисляется при чтении
```

`DEFAULT` — значение по умолчанию.

## Агрегатные типы

`AggregateFunction(...)`, `SimpleAggregateFunction(sum, UInt64)` для предагрегации.

## Кодеки и оптимизация размера

`CODEC(Delta, ZSTD)`, `CODEC(DoubleDelta)` для монотонных значений. Проверка размеров: `system.columns` (`data_compressed_bytes`, `data_uncompressed_bytes`).

```sql
SELECT name, formatReadableSize(data_compressed_bytes) AS comp, formatReadableSize(data_uncompressed_bytes) AS raw
FROM system.columns WHERE table = 'events' ORDER BY data_compressed_bytes DESC;
```

## Вопросы с ответами

> [!question]- Когда использовать LowCardinality?
> Для строк с малым числом уникальных значений (типы событий, страны, статусы, теги хостов). Уменьшает размер и ускоряет запросы; для высококардинальных значений вредно.

> [!question]- Почему Nullable не рекомендуется?
> Хранится дополнительный столбец маски, растёт объём данных, усложняются вычисления и снижается скорость. Часто достаточно значения по умолчанию.

> [!question]- Как хранить полуструктурированные данные?
> `Map`, тип `JSON` или строка + материализованные столбцы для часто запрашиваемых ключей.
