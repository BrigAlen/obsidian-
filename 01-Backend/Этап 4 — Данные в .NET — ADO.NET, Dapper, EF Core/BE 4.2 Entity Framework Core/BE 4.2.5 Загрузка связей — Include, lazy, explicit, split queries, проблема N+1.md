---
type: topic
domain: backend
stage: 4
section: "4.2"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981c1976ae85a151eb2fc
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, topic/performance, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Загрузка связей: Include, lazy, explicit, split queries, проблема N+1

↑ [[BE 4.2 Entity Framework Core|4.2 Entity Framework Core]] · ← [[BE 4.2.4 Change tracking — tracking и AsNoTracking, состояния сущностей|Предыдущая]] · → [[BE 4.2.6 Проекции, пагинация, сырой SQL, compiled queries|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






















































> [!info] Зачем это на собесе
> N+1 и cartesian explosion — самые частые проблемы производительности ORM. Ждут распознавания и решения.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Стратегия | Как | Плюс | Минус |
|---|---|---|---|
| Eager | `Include/ThenInclude` | один запрос | cartesian explosion при коллекциях |
| Split query | `AsSplitQuery()` | нет дублирования строк | несколько запросов, нет единого снимка |
| Explicit | `Entry(e).Collection(...).LoadAsync()` | контроль | ручной код |
| Lazy | прокси, `virtual` | «как будто всё загружено» | скрытый N+1 |
| Projection | `Select` в DTO | грузит только нужное | ручное описание |

### N+1

```csharp
// Плохо: 1 запрос за заказами + N запросов за клиентами (lazy loading или цикл)
foreach (var o in await db.Orders.ToListAsync())
    Console.WriteLine(o.Customer.Name);

// Хорошо
var orders = await db.Orders.Include(o => o.Customer).ToListAsync();
// Ещё лучше: проекция
var dtos = await db.Orders.Select(o => new { o.Id, CustomerName = o.Customer.Name }).ToListAsync();
```

### Cartesian explosion

`Include` двух коллекций даёт произведение строк: 100 заказов × 10 позиций × 5 платежей = 5000 строк. Решение: `AsSplitQuery()` или отдельные запросы/проекции.

```csharp
var orders = await db.Orders.Include(o => o.Items).Include(o => o.Payments).AsSplitQuery().ToListAsync();
```

## Нюансы и подводные камни

- Lazy loading лучше отключить: он скрывает запросы и ломает async.
- Фильтруемый `Include` (`Include(o => o.Items.Where(...))`) поддерживается.
- Логируйте SQL (`LogTo`) и считайте запросы на эндпоинт.
- Split query не атомарен: данные могут измениться между запросами.
- Загрузка всей сущности ради двух полей — лишние данные: используйте `Select`.

## Практика

1. Воспроизведите N+1 и найдите его в логах.
2. Исправьте тремя способами и сравните число запросов и время.
3. Найдите cartesian explosion и примените `AsSplitQuery`.

## Вопросы с ответами

> [!question]- Что такое проблема N+1?
> Один запрос за списком и по одному запросу на каждый элемент за связанными данными.

> [!question]- Когда нужен AsSplitQuery?
> При `Include` нескольких коллекций, чтобы избежать декартова произведения.

> [!question]- Почему lazy loading опасен?
> Запросы скрыты в обращениях к свойствам; легко получить N+1 и вызовы вне контекста.

## Связанные темы

- [[N:3ea331048679813da621c1c306b63386]]
- [[N:3ea3310486798149af8fc3f45a4ab5aa]]
