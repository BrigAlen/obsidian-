---
type: topic
domain: backend
stage: 4
section: "4.2"
order: 4
status: todo
level: middle
notion_id: 3ea331048679813da621c1c306b63386
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Change tracking: tracking и AsNoTracking, состояния сущностей

↑ [[BE 4.2 Entity Framework Core|4.2 Entity Framework Core]] · ← [[BE 4.2.3 Миграции EF Core|Предыдущая]] · → [[BE 4.2.5 Загрузка связей — Include, lazy, explicit, split queries, проблема N+1|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



























> [!info] Зачем это на собесе
> Ключевой механизм EF. Спрашивают, когда отключать tracking и что происходит при `SaveChanges`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Change tracker хранит снимки загруженных сущностей и при `SaveChanges` находит изменения, формируя UPDATE только для изменённых свойств.

| Состояние | Что произойдёт при SaveChanges |
|---|---|
| Detached | не отслеживается |
| Unchanged | ничего |
| Added | INSERT |
| Modified | UPDATE |
| Deleted | DELETE |

```csharp
var order = await db.Orders.FirstAsync(o => o.Id == id, ct);   // Unchanged
order.Status = Status.Paid;                                     // Modified
await db.SaveChangesAsync(ct);                                  // UPDATE orders SET status=... WHERE id=...

var list = await db.Orders.AsNoTracking().Where(...).ToListAsync(ct);   // чтение без трекинга
```

| Метод | Смысл |
|---|---|
| `AsNoTracking()` | быстрее и меньше памяти для read-only |
| `AsNoTrackingWithIdentityResolution()` | без tracking, но с единым экземпляром на ключ |
| `Attach`, `Update` | внедрить отсоединённую сущность (Update помечает все поля Modified) |
| `Entry(e).State` | ручное управление состоянием |
| `ChangeTracker.Clear()` | сброс трекера |

### Identity map

Запрос той же строки дважды в одном контексте вернёт **один и тот же объект**.

## Нюансы и подводные камни

- Для чтения списков по умолчанию используйте `AsNoTracking` (или `QueryTrackingBehavior.NoTracking`).
- `Update(entity)` обновит все колонки, включая не менявшиеся: возможна перезапись чужих изменений.
- Большие пачки сущностей в трекере замедляют `DetectChanges`.
- Изменение отслеживаемой сущности «вне» кода (в другом слое) может неожиданно попасть в SaveChanges.
- Для массового обновления используйте `ExecuteUpdate` (см. [[N:3ea33104867981c48e1fec4912a6ddf3]]).

## Практика

1. Сравните память и время `Include`-запроса с tracking и без.
2. Посмотрите `db.ChangeTracker.DebugView.LongView`.
3. Напишите обновление отсоединённой сущности безопасным способом.

## Вопросы с ответами

> [!question]- Когда использовать AsNoTracking?
> Для read-only запросов: меньше памяти и CPU, нет накладных расходов на снимки.

> [!question]- Что делает Update() на отсоединённой сущности?
> Присоединяет её и помечает все свойства изменёнными.

> [!question]- Что такое identity map?
> Гарантия одного экземпляра сущности на ключ в пределах контекста.

## Связанные темы

- [[N:3ea33104867981e88c8ffcdc0440cf35]]
- [[N:3ea33104867981c1976ae85a151eb2fc]]
