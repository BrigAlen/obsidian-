---
type: topic
domain: backend
stage: 4
section: "4.2"
order: 7
status: todo
level: middle
notion_id: 3ea33104867981c9990ec742caec5653
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, topic/concurrency, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Конкурентность: optimistic concurrency, xmin, row version

↑ [[BE 4.2 Entity Framework Core|4.2 Entity Framework Core]] · ← [[BE 4.2.6 Проекции, пагинация, сырой SQL, compiled queries|Предыдущая]] · → [[BE 4.2.8 Bulk-операции — ExecuteUpdate, ExecuteDelete, батчи|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





























> [!info] Зачем это на собесе
> «Что будет, если два пользователя редактируют одну запись?» — вопрос про потерянное обновление.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Lost update**: два пользователя прочитали одну версию, оба сохранили — последний затирает первого.

| Подход | Суть | Когда |
|---|---|---|
| Оптимистичная блокировка | проверка версии при UPDATE; при расхождении — ошибка | мало конфликтов, веб |
| Пессимистичная | `SELECT ... FOR UPDATE`, держит блокировку | высокая конкуренция, короткие операции |

```csharp
public class Order
{
    public Guid Id { get; set; }
    public uint Version { get; set; }   // PostgreSQL xmin
}

modelBuilder.Entity<Order>().Property(o => o.Version).IsRowVersion();   // Npgsql: xmin
// SQL Server: [Timestamp] byte[] RowVersion
```

EF добавляет условие `WHERE id = @id AND xmin = @version`; если строка не обновлена — `DbUpdateConcurrencyException`.

```csharp
try { await db.SaveChangesAsync(ct); }
catch (DbUpdateConcurrencyException)
{
    return Results.Conflict("Данные были изменены другим пользователем. Обновите страницу.");
}
```

### Клиент и ETag

Версия передаётся клиенту (`ETag`/поле) и возвращается в `If-Match`, чтобы конфликт обнаруживался между чтением и записью на UI.

### Пессимистичная

```csharp
var order = await db.Orders.FromSql($"select * from orders where id = {id} for update").SingleAsync();
```

## Нюансы и подводные камни

- Оптимистичная блокировка ничего не решает, если клиент не возвращает версию.
- Стратегия при конфликте: перечитать, объединить, спросить пользователя; не молча перезаписывать.
- Счётчики и балансы лучше обновлять атомарно `UPDATE ... SET balance = balance - @x` (ExecuteUpdate), а не read-modify-write.
- Для уникальности используйте unique-индексы и обрабатывайте нарушение.

## Практика

1. Добавьте `xmin` и воспроизведите конфликт двумя контекстами.
2. Верните 409 и `ETag` в API.
3. Реализуйте атомарное списание баланса.

## Вопросы с ответами

> [!question]- Оптимистичная или пессимистичная блокировка?
> Оптимистичная — при редких конфликтах и без удержания блокировок; пессимистичная — при частых конфликтах и критичных операциях.

> [!question]- Что такое xmin в PostgreSQL?
> Системная колонка с ID транзакции, создавшей версию строки; используется как токен конкурентности.

> [!question]- Как избежать lost update для счётчика?
> Атомарным SQL-выражением или сериализуемой транзакцией.

## Связанные темы

- [[N:3ea3310486798149af8fc3f45a4ab5aa]]
- [[N:3ea33104867981c48e1fec4912a6ddf3]]
