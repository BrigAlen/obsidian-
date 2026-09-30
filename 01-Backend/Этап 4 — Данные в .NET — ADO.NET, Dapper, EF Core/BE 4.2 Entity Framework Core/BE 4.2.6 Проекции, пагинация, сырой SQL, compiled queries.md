---
type: topic
domain: backend
stage: 4
section: "4.2"
order: 6
status: todo
level: middle
notion_id: 3ea3310486798149af8fc3f45a4ab5aa
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, topic/queries, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Проекции, пагинация, сырой SQL, compiled queries

↑ [[BE 4.2 Entity Framework Core|4.2 Entity Framework Core]] · ← [[BE 4.2.5 Загрузка связей — Include, lazy, explicit, split queries, проблема N+1|Предыдущая]] · → [[BE 4.2.7 Конкурентность — optimistic concurrency, xmin, row version|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->







































> [!info] Зачем это на собесе
> Проверяет практические навыки написания эффективных запросов и знание, где LINQ не хватает.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### Проекции

```csharp
var page = await db.Orders
    .Where(o => o.Status == Status.Paid)
    .Select(o => new OrderListItem(o.Id, o.Number, o.Customer.Name, o.Items.Sum(i => i.Price * i.Qty)))
    .ToListAsync(ct);
```

EF транслирует в SQL только нужные колонки и агрегаты.

### Пагинация

| Способ | SQL | Плюсы/минусы |
|---|---|---|
| Offset | `OFFSET n LIMIT m` | просто, медленно на больших offset, «прыгающие» страницы |
| Keyset (seek) | `WHERE (created, id) < (@c, @i) ORDER BY ... LIMIT m` | стабильно быстро, нет произвольной страницы |

```csharp
var items = await db.Orders
    .OrderByDescending(o => o.CreatedAt).ThenByDescending(o => o.Id)
    .Where(o => o.CreatedAt < cursor.CreatedAt || (o.CreatedAt == cursor.CreatedAt && o.Id < cursor.Id))
    .Take(pageSize + 1)   // +1 — определить, есть ли следующая страница
    .ToListAsync(ct);
```

Всегда задавайте детерминированную сортировку (уникальное поле в конце).

### Сырой SQL

```csharp
var rows = await db.Database.SqlQuery<StatRow>($"select status, count(*) as cnt from orders group by status").ToListAsync();
var orders = await db.Orders.FromSql($"select * from orders where status = {status}").ToListAsync();
```

### Compiled queries

```csharp
static readonly Func<AppDbContext, Guid, Task<Order?>> GetById =
    EF.CompileAsyncQuery((AppDbContext db, Guid id) => db.Orders.FirstOrDefault(o => o.Id == id));
```

Убирают стоимость трансляции выражения в горячих путях; выигрыш заметен на очень частых простых запросах.

## Нюансы и подводные камни

- `ToList()` до `Where` переносит фильтрацию в память (client evaluation): всё загружается.
- Методы, которые нельзя перевести в SQL, вызывают исключение или клиентскую оценку в проекции.
- Count на больших таблицах для «всего страниц» дорог: рассмотрите оценку.
- Индексы под ORDER BY и фильтры критичны.
- `Contains` с большими списками порождает огромные IN.

## Практика

1. Замените offset пагинацию на keyset и измерьте на 5 млн строк.
2. Сделайте отчёт `group by` через проекцию и через SqlQuery.
3. Скомпилируйте горячий запрос и замерьте BenchmarkDotNet.

## Вопросы с ответами

> [!question]- Offset или keyset?
> Keyset быстрее и стабильнее на больших данных, но не даёт прыжков на произвольную страницу; offset прост, но деградирует.

> [!question]- Зачем проекции?
> Загружают только нужные колонки, нет tracking и лишних данных.

> [!question]- Когда FromSql вместо LINQ?
> Для сложных запросов (CTE, оконные функции), функций БД и оптимизации; значения — только параметрами.

## Связанные темы

- [[N:3ea33104867981c1976ae85a151eb2fc]]
- [[N:3ea33104867981c9990ec742caec5653]]
