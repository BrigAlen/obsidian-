---
type: topic
domain: backend
stage: 4
section: "4.2"
order: 10
status: todo
level: middle
notion_id: 3ea33104867981048155ce6c5ea28bef
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, topic/architecture, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Repository и Unit of Work поверх EF: нужно ли

↑ [[BE 4.2 Entity Framework Core|4.2 Entity Framework Core]] · ← [[BE 4.2.9 Производительность EF Core и логирование SQL|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

























> [!info] Зачем это на собесе
> Спорная тема: ответ «зависит» с аргументами лучше догмы.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`DbContext` уже реализует Unit of Work, а `DbSet<T>` — Repository. Обёртка над ними ради самой обёртки часто бесполезна.

| Подход | Плюсы | Минусы |
|---|---|---|
| Напрямую `DbContext` в handlers | просто, полный LINQ и Include | зависимость от EF, тестируется интеграционно |
| Generic Repository (`IRepository<T>`) | единый интерфейс | «протекающая абстракция», обрезает возможности EF |
| Специфичные репозитории (`IOrderRepository`) | доменный язык, скрывает запросы | больше кода |
| Specification pattern | переиспользуемые условия | усложнение |

Разумный вариант: репозитории агрегатов в DDD-стиле (загрузка/сохранение агрегата целиком) + отдельные read-модели/запросы (CQRS) напрямую через EF или Dapper.

```csharp
public interface IOrderRepository
{
    Task<Order?> GetAsync(Guid id, CancellationToken ct);   // агрегат с позициями
    void Add(Order order);
}

public class OrderRepository(AppDbContext db) : IOrderRepository
{
    public Task<Order?> GetAsync(Guid id, CancellationToken ct) => db.Orders.Include(o => o.Items).FirstOrDefaultAsync(o => o.Id == id, ct);
    public void Add(Order order) => db.Orders.Add(order);
}
// Unit of Work = DbContext.SaveChangesAsync в handler/behavior
```

## Нюансы и подводные камни

- Generic-репозиторий с `IQueryable` наружу не скрывает EF, но добавляет слой.
- Репозиторий, возвращающий `IEnumerable` с `GetAll()`, приводит к загрузке таблицы.
- Мок репозитория не проверяет запросы: важнее интеграционные тесты.
- Транзакция и `SaveChanges` — ответственность use case, а не репозитория.

## Практика

1. Уберите generic-репозиторий из проекта и сравните объём кода.
2. Реализуйте репозиторий агрегата и read-модель для списка.
3. Проведите ревью: где абстракция помогает, а где мешает.

## Вопросы с ответами

> [!question]- Нужен ли Repository поверх EF Core?
> Не всегда: DbContext уже Repository + Unit of Work. Репозиторий оправдан для агрегатов и тестируемой границы, но generic-обёртка обычно лишняя.

> [!question]- Где вызывать SaveChanges?
> На уровне use case/handler, чтобы одна бизнес-операция была одной транзакцией.

> [!question]- Что такое Specification?
> Инкапсуляция условия запроса в объект для повторного использования.

## Связанные темы

- [[N:3ea3310486798111a4bafaf4f54018b5]]
- [[N:3ea33104867981df8306e2ce8ba91fbb]]
