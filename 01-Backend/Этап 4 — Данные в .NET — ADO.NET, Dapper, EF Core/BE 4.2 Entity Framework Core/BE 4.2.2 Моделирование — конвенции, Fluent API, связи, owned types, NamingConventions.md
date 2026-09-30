---
type: topic
domain: backend
stage: 4
section: "4.2"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981bfbfc4ec436ba6c342
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, topic/modeling, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Моделирование: конвенции, Fluent API, связи, owned types, NamingConventions

↑ [[BE 4.2 Entity Framework Core|4.2 Entity Framework Core]] · ← [[BE 4.2.1 DbContext — жизненный цикл, pooling, Unit of Work|Предыдущая]] · → [[BE 4.2.3 Миграции EF Core|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->































> [!info] Зачем это на собесе
> Проверяют, умеете ли вы описать связи и не «размазывать» конфигурацию по атрибутам.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Три источника конфигурации (по возрастанию приоритета): конвенции → атрибуты → Fluent API.

```csharp
public class OrderConfig : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> b)
    {
        b.ToTable("orders");
        b.HasKey(x => x.Id);
        b.Property(x => x.Number).HasMaxLength(32).IsRequired();
        b.HasIndex(x => x.Number).IsUnique();
        b.HasOne(x => x.Customer).WithMany(c => c.Orders).HasForeignKey(x => x.CustomerId).OnDelete(DeleteBehavior.Restrict);
        b.OwnsOne(x => x.ShippingAddress);                        // owned type (value object)
        b.Property(x => x.Status).HasConversion<string>();        // enum → строка
        b.HasQueryFilter(x => !x.IsDeleted);                      // soft delete
    }
}
```

| Связь | Настройка |
|---|---|
| 1:N | `HasOne().WithMany()` |
| 1:1 | `HasOne().WithOne()` + внешний ключ |
| N:M | skip navigation `HasMany().WithMany()` (таблица связи создаётся автоматически) |
| Owned | `OwnsOne/OwnsMany`, хранится в той же таблице/JSON |

### Соглашение об именах

```csharp
options.UseNpgsql(cs).UseSnakeCaseNamingConvention();   // EFCore.NamingConventions
```

Даёт `customer_id`, `order_items` вместо `CustomerId`, `OrderItems` — идиоматичный PostgreSQL.

### Прочее

- Value converters (`Guid`↔`string`, `DateOnly`), shadow properties, TPH/TPT/TPC наследование, JSON-колонки (`OwnsOne(...).ToJson()`).
- Global query filters — soft delete и multi-tenancy; отключаются `IgnoreQueryFilters()`.

## Нюансы и подводные камни

- Каскадное удаление по умолчанию для обязательных связей — явно задавайте `OnDelete`.
- Nullable reference types влияют на обязательность колонок.
- Свойство-коллекция без конструктора для EF: используйте приватный ctor и backing field.
- TPH по умолчанию (одна таблица с discriminator), TPT дороже по join.
- `decimal` без точности даёт предупреждение: `HasPrecision(18, 2)`.

## Практика

1. Опишите заказ, клиента, позиции, адрес (owned) через `IEntityTypeConfiguration`.
2. Добавьте soft delete через query filter.
3. Настройте snake_case и сравните SQL.

## Вопросы с ответами

> [!question]- Что такое owned type?
> Value object без своей идентичности, хранится вместе с владельцем (в той же таблице или как JSON).

> [!question]- TPH, TPT, TPC — в чём отличие?
> TPH — одна таблица, TPT — таблица на тип с join-ами, TPC — таблица на конкретный тип без общей.

> [!question]- Зачем IEntityTypeConfiguration?
> Держит конфигурацию сущности отдельно, `OnModelCreating` остаётся компактным.

## Связанные темы

- [[N:3ea33104867981c7a0d3ffbde71096db]]
- [[N:3ea33104867981e88c8ffcdc0440cf35]]
