---
type: topic
domain: backend
stage: 4
section: "4.2"
order: 8
status: todo
level: middle
notion_id: 3ea33104867981c48e1fec4912a6ddf3
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, topic/performance, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Bulk-операции: ExecuteUpdate, ExecuteDelete, батчи

↑ [[BE 4.2 Entity Framework Core|4.2 Entity Framework Core]] · ← [[BE 4.2.7 Конкурентность — optimistic concurrency, xmin, row version|Предыдущая]] · → [[BE 4.2.9 Производительность EF Core и логирование SQL|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




























> [!info] Зачем это на собесе
> Как быстро обновить или вставить много записей, не загружая их в память.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

С EF Core 7 массовые операции выполняются одним SQL без загрузки сущностей и без tracking.

```csharp
await db.Orders.Where(o => o.Status == Status.Draft && o.CreatedAt < cutoff).ExecuteDeleteAsync(ct);

await db.Products.Where(p => p.CategoryId == cid)
    .ExecuteUpdateAsync(s => s
        .SetProperty(p => p.Price, p => p.Price * 1.1m)
        .SetProperty(p => p.UpdatedAt, DateTime.UtcNow), ct);
```

| Задача | Инструмент |
|---|---|
| Обновить/удалить по условию | `ExecuteUpdate/ExecuteDelete` |
| Пачка INSERT из EF | `AddRange` + `SaveChanges` (батчи по умолчанию) |
| Очень много строк (100 тыс.+) | `COPY` (Npgsql binary import), `EFCore.BulkExtensions` |

```csharp
await using var writer = await conn.BeginBinaryImportAsync("copy items (id, name) from stdin (format binary)", ct);
foreach (var i in items) { await writer.StartRowAsync(ct); await writer.WriteAsync(i.Id, ct); await writer.WriteAsync(i.Name, ct); }
await writer.CompleteAsync(ct);
```

## Нюансы и подводные камни

- `ExecuteUpdate` обходит change tracker: уже загруженные сущности в контексте устаревают.
- Не срабатывают события/логика `SaveChanges` (интерсепторы, аудит, версионирование).
- Огромные `UPDATE` блокируют строки и раздувают WAL: дробите на порции.
- Размер батча EF (`MaxBatchSize`) и лимит параметров PostgreSQL (65535).
- Большие вставки в одной транзакции держат её долго.

## Практика

1. Замените цикл загрузки-обновления на `ExecuteUpdate`.
2. Вставьте 1 млн строк через `COPY` и сравните с `AddRange`.
3. Реализуйте удаление старых записей порциями по 10 000.

## Вопросы с ответами

> [!question]- Чем ExecuteUpdate лучше загрузки и SaveChanges?
> Один SQL на сервере, без передачи данных и tracking — на порядки быстрее для массовых операций.

> [!question]- Что теряется при ExecuteUpdate?
> Логика SaveChanges: аудит, интерсепторы, оптимистичная конкуренция.

> [!question]- Как быстро загрузить очень много данных в PostgreSQL?
> Binary `COPY` через Npgsql.

## Связанные темы

- [[N:3ea33104867981c9990ec742caec5653]]
- [[N:3ea3310486798111a4bafaf4f54018b5]]
