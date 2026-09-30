---
type: topic
domain: backend
stage: 4
section: "4.2"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981c7a0d3ffbde71096db
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# DbContext: жизненный цикл, pooling, Unit of Work

↑ [[BE 4.2 Entity Framework Core|4.2 Entity Framework Core]] · → [[BE 4.2.2 Моделирование — конвенции, Fluent API, связи, owned types, NamingConventions|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> DbContext — центральный объект EF. Спрашивают, почему он scoped, потокобезопасен ли, и что такое Unit of Work.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`DbContext` — это одновременно **Unit of Work** (накапливает изменения и сохраняет одной транзакцией в `SaveChanges`) и **Repository** (через `DbSet<T>`), а также хранит **change tracker** с загруженными сущностями (identity map).

```csharp
public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<Order> Orders => Set<Order>();
    protected override void OnModelCreating(ModelBuilder b) => b.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
}

builder.Services.AddDbContext<AppDbContext>(o => o.UseNpgsql(cs));       // scoped
builder.Services.AddDbContextPool<AppDbContext>(o => o.UseNpgsql(cs));   // пул экземпляров
builder.Services.AddDbContextFactory<AppDbContext>(o => o.UseNpgsql(cs)); // для singleton/фона
```

| Вариант | Когда |
|---|---|
| `AddDbContext` (scoped) | обычные веб-запросы |
| `AddDbContextPool` | высокая нагрузка: экземпляры переиспользуются, состояние сбрасывается |
| `IDbContextFactory<T>` | фоновые задачи, Blazor Server, параллельные операции |

### Unit of Work

```csharp
var order = new Order(...);
db.Orders.Add(order);
var customer = await db.Customers.FindAsync(id);
customer.Rename("X");
await db.SaveChangesAsync(ct);   // один набор INSERT/UPDATE в одной транзакции
```

## Нюансы и подводные камни

- DbContext **не потокобезопасен**: один контекст — один поток/логическая операция; `Task.WhenAll` с одним контекстом ломается.
- Долго живущий контекст накапливает сущности в трекере и растёт в памяти.
- При использовании pooling нельзя хранить в контексте состояние запроса (tenant, пользователь) в полях.
- Не создавайте контекст в цикле на каждую операцию без необходимости.
- `SaveChanges` выполняется одной транзакцией по умолчанию; несколько вызовов — несколько транзакций.

## Практика

1. Включите `AddDbContextPool` и замерьте разницу на нагрузочном тесте.
2. Реализуйте фоновый обработчик через `IDbContextFactory`.
3. Убедитесь, что 2 параллельных запроса через один контекст падают.

## Вопросы с ответами

> [!question]- Почему DbContext scoped?
> Он не потокобезопасен и хранит состояние (tracker); живёт на время одной логической операции/запроса.

> [!question]- В чём смысл pooling?
> Переиспользуются экземпляры контекста и их внутренние сервисы; снижаются аллокации.

> [!question]- Является ли DbContext Unit of Work?
> Да: накапливает изменения и сохраняет их атомарно в `SaveChanges`.

## Связанные темы

- [[N:3ea331048679810c9828c6cb489c659b]]
- [[N:3ea33104867981bfbfc4ec436ba6c342]]
