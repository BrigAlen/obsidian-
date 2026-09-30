---
type: topic
domain: backend
stage: 3
section: "3.2"
order: 2
status: todo
level: middle
notion_id: 3ea331048679815b938fd2f3f2a7c66d
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/di, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Время жизни: Singleton, Scoped, Transient

↑ [[BE 3.2 Dependency Injection|3.2 Dependency Injection]] · ← [[BE 3.2.1 DI и IoC — зачем и как работает контейнер|Предыдущая]] · → [[BE 3.2.3 Captive dependency и другие ловушки DI|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













































> [!info] Зачем это на собесе
> Обязательный вопрос. Ждут не определений, а примеров: что сделать singleton-ом, что scoped-ом и что ломается при ошибке.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Время жизни | Экземпляров | Типичное применение |
|---|---|---|
| Singleton | один на приложение | кэш, фабрики, `HttpClient`-обёртки, конфигурация, без состояния |
| Scoped | один на scope (в вебе — на HTTP-запрос) | `DbContext`, unit of work, контекст пользователя |
| Transient | новый при каждом запросе к контейнеру | лёгкие stateless сервисы |

```csharp
builder.Services.AddSingleton<IClock, SystemClock>();
builder.Services.AddScoped<AppDbContext>();
builder.Services.AddTransient<IEmailBuilder, EmailBuilder>();
```

### Правила зависимостей

Сервис может зависеть от сервисов **с таким же или более длинным** временем жизни:

| Кто \ От кого | Singleton | Scoped | Transient |
|---|---|---|---|
| Singleton | да | нет (captive) | осторожно |
| Scoped | да | да | да |
| Transient | да | да | да |

### Scope вне запроса

В фоновом сервисе scope нужно создавать вручную:

```csharp
using var scope = scopeFactory.CreateScope();
var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
```

### Освобождение

Контейнер вызывает `Dispose/DisposeAsync` у объектов, которые сам создал. Экземпляр, зарегистрированный готовым (`AddSingleton(instance)`), контейнер не освобождает.

## Нюансы и подводные камни

- Singleton со статичным состоянием обязан быть потокобезопасным.
- Transient `IDisposable` в singleton накапливается до конца приложения (утечка).
- `DbContext` — не потокобезопасный, только scoped.
- В Development включается `ValidateScopes` и `ValidateOnBuild`, помогая находить ошибки.

## Практика

1. Выведите `GetHashCode()` сервисов в трёх временах жизни на нескольких запросах.
2. Внедрите scoped в singleton и посмотрите ошибку валидации.
3. Создайте scope в `BackgroundService`.

## Вопросы с ответами

> [!question]- Что значит scoped в ASP.NET Core?
> Один экземпляр на HTTP-запрос: контейнер создаёт scope на запрос и освобождает его в конце.

> [!question]- Можно ли внедрить scoped в singleton?
> Нет, получится captive dependency: scoped-объект «застрянет» на время жизни singleton.

> [!question]- Что выбрать по умолчанию?
> Для stateless-сервисов подходят все; Singleton — если сервис потокобезопасен и дорог в создании; Scoped — если хранит контекст запроса.

## Связанные темы

- [[N:3ea33104867981d7abcbd600756a8323]]
- [[N:3ea33104867981d2bc3bc47bf945c910]]
