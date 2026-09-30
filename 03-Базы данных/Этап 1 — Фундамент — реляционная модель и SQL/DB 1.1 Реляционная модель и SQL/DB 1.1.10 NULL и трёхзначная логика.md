---
type: topic
domain: db
stage: 1
section: "1.1"
order: 10
status: todo
level: junior
notion_id: 3ea33104867981419dd5c1d6081a8eae
tags: [domain/db, stage/1, level/junior, topic/sql, topic/null, topic/logic, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# NULL и трёхзначная логика

↑ [[DB 1.1 Реляционная модель и SQL|1.1 Реляционная модель и SQL]] · ← [[DB 1.1.9 INSERT, UPDATE, DELETE, UPSERT (ON CONFLICT), RETURNING|Предыдущая]] · → [[DB 1.1.11 Задачи на SQL с собеседований|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> NULL — источник самых неочевидных ошибок; на нём строят каверзные вопросы.

## Что такое NULL

**Отсутствие значения / неизвестное значение**, а не ноль и не пустая строка. Любое сравнение с NULL даёт **UNKNOWN**.

## Трёхзначная логика

| A | B | A AND B | A OR B |
|---|---|---|---|
| TRUE | UNKNOWN | UNKNOWN | TRUE |
| FALSE | UNKNOWN | FALSE | UNKNOWN |
| UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |

`NOT UNKNOWN` — UNKNOWN. `WHERE` пропускает **только TRUE**, строки с UNKNOWN отбрасываются.

```sql
SELECT NULL = NULL;        -- NULL (не true)
SELECT NULL IS NULL;       -- true
SELECT 1 = NULL;           -- NULL
SELECT NULL IS DISTINCT FROM NULL;   -- false (NULL-безопасное сравнение)
```

## Правила

- проверка: `IS NULL` / `IS NOT NULL`, а не `= NULL`;
- `x <> 5` не вернёт строки, где `x IS NULL`; нужно `x IS DISTINCT FROM 5`;
- `NOT IN` с NULL в списке — пустой результат; используйте `NOT EXISTS`;
- арифметика и конкатенация с NULL дают NULL (`'a' || NULL` → NULL, функция `concat` игнорирует NULL);
- агрегаты (`sum`, `avg`, `count(col)`) игнорируют NULL; `count(*)` — нет;
- `ORDER BY`: NULL считаются больше любого значения (`NULLS LAST` по умолчанию при ASC);
- `GROUP BY`, `DISTINCT`, `UNION` **считают NULL равными** между собой;
- `UNIQUE` допускает несколько NULL (можно отключить через `NULLS NOT DISTINCT`, PostgreSQL 15+);
- `CHECK` пропускает NULL (UNKNOWN не нарушает ограничение): ставьте `NOT NULL`.

## Функции

```sql
coalesce(a, b, 'по умолчанию')   -- первое не-NULL
nullif(a, 0)                     -- NULL, если a = 0 (защита от деления на ноль: x / nullif(y, 0))
a IS DISTINCT FROM b
```

## Когда NULL допустим

Реально «неизвестно» или «неприменимо» (дата закрытия у открытого тикета). Избегайте NULL для флагов (используйте `boolean NOT NULL DEFAULT false`) и там, где есть осмысленное значение по умолчанию.

## Индексы

B-tree индексирует NULL (можно искать `IS NULL`). Частичный индекс `WHERE deleted_at IS NULL` — частый приём.

## Вопросы с ответами

> [!question]- Почему `WHERE col <> 5` не находит строки с NULL?
> Сравнение NULL с 5 даёт UNKNOWN, а WHERE берёт только TRUE. Нужно `col IS DISTINCT FROM 5` или явно `OR col IS NULL`.

> [!question]- Что вернёт `SELECT count(*), count(col)` для таблицы с NULL?
> `count(*)` — все строки, `count(col)` — только строки, где `col` не NULL.

> [!question]- Как защититься от деления на ноль?
> `x / nullif(y, 0)` вернёт NULL вместо ошибки; при необходимости обернуть в `coalesce`.
