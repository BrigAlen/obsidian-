---
type: topic
domain: backend
stage: 3
section: "3.2"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981d7abcbd600756a8323
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/di, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# DI и IoC: зачем и как работает контейнер

↑ [[BE 3.2 Dependency Injection|3.2 Dependency Injection]] · → [[BE 3.2.2 Время жизни — Singleton, Scoped, Transient|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




























> [!info] Зачем это на собесе
> Базовый вопрос: «что такое DI, чем отличается от IoC и зачем контейнер». Дальше почти всегда идут времена жизни.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

- **IoC (Inversion of Control)** — принцип: не класс создаёт свои зависимости, а внешний код передаёт их.
- **DI (Dependency Injection)** — способ реализации IoC: зависимости передаются через конструктор (предпочтительно), свойство или параметр метода.
- **DI-контейнер** — инструмент, который по регистрациям строит граф объектов и управляет временем жизни.

```csharp
// Без DI: жёсткая связь
public class OrderService { private readonly SqlRepo _repo = new SqlRepo(); }

// С DI: зависимость от абстракции
public class OrderService(IOrderRepository repo, ILogger<OrderService> log) { }

builder.Services.AddScoped<IOrderRepository, SqlOrderRepository>();
builder.Services.AddScoped<OrderService>();
```

| Выгода | Пояснение |
|---|---|
| Слабая связность | реализация заменяется без правки клиента |
| Тестируемость | подставляются fake/stub |
| Единое место сборки | композиционный корень в `Program.cs` |
| Управление временем жизни | контейнер создаёт и освобождает объекты |

### Как работает встроенный контейнер

`ServiceProvider` находит конструктор с максимальным числом разрешимых параметров, рекурсивно строит зависимости, кэширует экземпляры по времени жизни, вызывает `Dispose` у созданных им `IDisposable` при закрытии scope. Поддерживает open generics: `AddScoped(typeof(IRepo<>), typeof(Repo<>))` и `IEnumerable<T>` для нескольких реализаций.

## Нюансы и подводные камни

- Constructor injection лучше property injection: зависимости явны и обязательны.
- Service Locator (`IServiceProvider.GetService` в бизнес-коде) — антипаттерн, скрывает зависимости.
- Много параметров конструктора — сигнал нарушения SRP.
- Встроенный контейнер не умеет property injection, interceptors и автоматические декораторы (для этого Autofac/Scrutor).
- Циклические зависимости приводят к исключению при построении.

## Практика

1. Уберите `new` из сервиса и зарегистрируйте зависимости.
2. Зарегистрируйте несколько реализаций интерфейса и получите `IEnumerable<T>`.
3. Напишите open generic репозиторий.

## Вопросы с ответами

> [!question]- Чем DI отличается от IoC?
> IoC — принцип инверсии управления; DI — конкретный приём передачи зависимостей извне.

> [!question]- Зачем нужен DI-контейнер, если можно вручную передавать зависимости?
> На больших графах контейнер убирает шаблонный код, управляет временем жизни и освобождением объектов.

> [!question]- Что такое композиционный корень?
> Место, где строится граф зависимостей (Program.cs); остальной код не знает о контейнере.

## Связанные темы

- [[N:3ea331048679815b938fd2f3f2a7c66d]]
- [[N:3ea33104867981d2bc3bc47bf945c910]]
