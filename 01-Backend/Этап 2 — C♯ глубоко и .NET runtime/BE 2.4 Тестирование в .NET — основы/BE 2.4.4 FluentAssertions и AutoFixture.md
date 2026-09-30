---
type: topic
domain: backend
stage: 2
section: "2.4"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981c6ad5ae1bb29d7bce3
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/testing, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# FluentAssertions и AutoFixture

↑ [[BE 2.4 Тестирование в .NET — основы|2.4 Тестирование в .NET — основы]] · ← [[BE 2.4.3 Тестовые двойники — Moq и NSubstitute|Предыдущая]] · → [[BE 2.4.5 Тестируемый код — DI, TimeProvider, границы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->































> [!info] Зачем это на собесе
> Меньший приоритет, но показывает опыт: как сделать проверки читаемыми и не писать вручную длинные тестовые данные.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### FluentAssertions (и Shouldly)

Читаемые проверки с осмысленными сообщениями при падении.

```csharp
result.Should().NotBeNull();
result.Items.Should().HaveCount(3).And.OnlyContain(i => i.Price > 0);
order.Should().BeEquivalentTo(expected, o => o.Excluding(x => x.CreatedAt));

await FluentActions.Awaiting(() => sut.PayAsync(order))
    .Should().ThrowAsync<PaymentException>().WithMessage("*declined*");
```

`BeEquivalentTo` сравнивает объекты структурно, что удобно для DTO и графов.

> [!warning] Лицензия
> Начиная с 8-й версии FluentAssertions распространяется по коммерческой лицензии для коммерческого использования. Альтернативы: Shouldly, AwesomeAssertions (форк версии 7).

### AutoFixture

Генерирует значения для тестовых данных, чтобы не заполнять вручную ненужные поля.

```csharp
var fixture = new Fixture();
var order = fixture.Build<Order>()
    .With(o => o.Status, OrderStatus.New)
    .Create();

var items = fixture.CreateMany<OrderItem>(5).ToList();
```

С `AutoFixture.Xunit2`: `[Theory, AutoData] void Test(Order order)`. С `AutoMoq`/`AutoNSubstitute` фикстура ещё и подставляет зависимости SUT.

### Builder как альтернатива

```csharp
var order = new OrderBuilder().WithItems(3).Paid().Build();
```

Явные builder-ы делают тест понятным: видно только значимые для сценария поля.

## Нюансы и подводные камни

- Случайные данные усложняют воспроизведение: логируйте seed или фиксируйте значимые поля явно.
- `BeEquivalentTo` может «проглатывать» несовпадение, если конфигурация слишком мягкая.
- Слишком много магии AutoFixture скрывает суть теста.
- Тест должен показывать, что важно: важные значения задавайте явно, остальное генерируйте.

## Практика

1. Перепишите три теста, заменив `Assert.Equal` на fluent-проверки и сравните сообщения об ошибках.
2. Сгенерируйте 100 заказов через AutoFixture и проверьте инвариант.
3. Напишите builder для сложной сущности.

## Вопросы с ответами

> [!question]- Зачем нужен BeEquivalentTo?
> Структурное сравнение объектов по значениям свойств, а не по ссылке, с гибкой настройкой исключений.

> [!question]- Чем плохи случайные тестовые данные?
> Нестабильно воспроизводятся падения и скрывается, какие значения важны для сценария.

> [!question]- Builder или AutoFixture?
> Builder явнее и читабельнее, AutoFixture быстрее при большом числе полей; часто используют вместе.

## Связанные темы

- [[N:3ea33104867981b18627d30f782b4713]]
- [[N:3ea33104867981a2ad5ff285f83ecce9]]
