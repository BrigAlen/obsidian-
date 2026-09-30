---
type: topic
domain: backend
stage: 2
section: "2.4"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981a2ad5ff285f83ecce9
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/testing, topic/design, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Тестируемый код: DI, TimeProvider, границы

↑ [[BE 2.4 Тестирование в .NET — основы|2.4 Тестирование в .NET — основы]] · ← [[BE 2.4.4 FluentAssertions и AutoFixture|Предыдущая]] · → [[BE 2.4.6 Coverage (coverlet) и CI|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




















> [!info] Зачем это на собесе
> Проверка проектного мышления: почему код «не тестируется» и как это исправить не моками, а дизайном.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Код плохо тестируется, когда логика смешана с побочными эффектами и скрытыми зависимостями: `DateTime.Now`, `new HttpClient()`, статика, синглтоны, `Random`.

| Проблема | Решение |
|---|---|
| Текущее время | `TimeProvider` (.NET 8) + `FakeTimeProvider` |
| Случайность и Guid | внедрять источник или seed |
| Файловая система, сеть | абстракция на границе или реальная зависимость в интеграционном тесте |
| Статические вызовы | обёртка или перенос в композиционный корень |
| Бизнес-логика вместе с I/O | «функциональное ядро, императивная оболочка» |

```csharp
public class TokenService(TimeProvider clock)
{
    public bool IsExpired(Token t) => t.ExpiresAt <= clock.GetUtcNow();
}

// в тесте
var time = new FakeTimeProvider(new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero));
var sut = new TokenService(time);
time.Advance(TimeSpan.FromHours(2));
Assert.True(sut.IsExpired(token));
```

### Функциональное ядро

Чистая логика принимает данные и возвращает решение, оболочка читает и пишет данные. Ядро тестируется без моков.

```csharp
// чистая функция
static Decision Evaluate(Order o, DateTimeOffset now) => /* ... */;

// оболочка
public async Task HandleAsync(Guid id, CancellationToken ct)
{
    var order = await repo.GetAsync(id, ct);
    var decision = Evaluate(order, clock.GetUtcNow());
    await repo.SaveAsync(decision, ct);
}
```

## Нюансы и подводные камни

- Конструктор с 10 зависимостями — признак нарушения SRP, а не проблемы тестов.
- Не выносите в интерфейс всё подряд: интерфейс ради мока без второй реализации лишний.
- Service locator и статический доступ к контейнеру скрывают зависимости.
- `internal` члены можно открыть тестам через `InternalsVisibleTo`, но лучше тестировать публичное поведение.

## Практика

1. Замените `DateTime.UtcNow` в проекте на `TimeProvider`.
2. Выделите чистую функцию из метода с I/O и покройте её табличными тестами.
3. Найдите класс с максимальным числом зависимостей и разбейте.

## Вопросы с ответами

> [!question]- Как протестировать код, зависящий от времени?
> Внедрить `TimeProvider` и использовать `FakeTimeProvider`, управляя временем в тесте.

> [!question]- Что такое композиционный корень?
> Единственное место (обычно `Program.cs`), где собирается граф зависимостей; остальной код получает зависимости через конструктор.

> [!question]- Сколько интерфейсов нужно для тестируемости?
> Столько, сколько границ с внешним миром; интерфейс на каждый класс — избыточен.

## Связанные темы

- [[N:3ea33104867981c6ad5ae1bb29d7bce3]]
- [[N:3ea331048679819b872aecead9568ecf]]
