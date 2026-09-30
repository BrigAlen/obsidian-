---
type: topic
domain: backend
stage: 3
section: "3.1"
order: 4
status: todo
level: middle
notion_id: 3ea331048679814dbaadc2a67ef314e5
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/configuration, topic/options, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Options pattern: IOptions, IOptionsSnapshot, IOptionsMonitor, валидация

↑ [[BE 3.1 Хост, конфигурация и middleware pipeline|3.1 Хост, конфигурация и middleware pipeline]] · ← [[BE 3.1.3 Конфигурация — appsettings, окружения, переменные, секреты|Предыдущая]] · → [[BE 3.1.5 Логирование — ILogger, уровни, structured logging, Serilog|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> Разница между тремя интерфейсами Options и умение включить валидацию на старте — типичный вопрос на middle.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Options pattern привязывает секцию конфигурации к типизированному классу.

```csharp
public class JwtOptions
{
    public const string Section = "Jwt";
    [Required] public string Issuer { get; init; } = "";
    [Required, MinLength(32)] public string Key { get; init; } = "";
    [Range(1, 1440)] public int LifetimeMinutes { get; init; } = 60;
}

builder.Services
    .AddOptions<JwtOptions>()
    .Bind(builder.Configuration.GetSection(JwtOptions.Section))
    .ValidateDataAnnotations()
    .ValidateOnStart();
```

| Интерфейс | Время жизни | Обновление | Когда |
|---|---|---|---|
| `IOptions<T>` | singleton | не обновляется | статичные настройки |
| `IOptionsSnapshot<T>` | scoped | обновляется на каждый запрос | веб-запросы с перечитыванием |
| `IOptionsMonitor<T>` | singleton | обновляется, есть `OnChange` | фоновые сервисы, singleton-ы |

```csharp
public class TokenService(IOptionsMonitor<JwtOptions> opts)
{
    public string Issuer => opts.CurrentValue.Issuer;   // всегда свежее значение
}
```

### Именованные options и ValidateOnStart

`Configure<T>("name", ...)` и `IOptionsMonitor<T>.Get("name")` позволяют держать несколько конфигураций одного типа (несколько клиентов, провайдеров). `ValidateOnStart()` роняет приложение при старте с понятной ошибкой, а не при первом обращении.

## Нюансы и подводные камни

- `IOptionsSnapshot` нельзя внедрять в singleton (scoped внутри singleton — captive dependency).
- Для `init`/`required`-свойств и привязки используйте `BindConfiguration` или `Bind`.
- Без `ValidateOnStart` ошибки конфигурации проявятся на проде при первом запросе.
- Сложную валидацию делайте через `IValidateOptions<T>`.
- Не внедряйте `IConfiguration` в бизнес-код: сложно тестировать и нет типов.

## Практика

1. Оформите секцию `Smtp` как Options с валидацией и `ValidateOnStart`.
2. Измените appsettings на лету и проследите, как ведут себя Snapshot и Monitor.
3. Напишите `IValidateOptions<T>` с зависимой проверкой (если `UseTls`, то `Port` не 25).

## Вопросы с ответами

> [!question]- Чем IOptions, IOptionsSnapshot и IOptionsMonitor отличаются?
> `IOptions` читается один раз и живёт как singleton; `IOptionsSnapshot` — scoped, перечитывается на запрос; `IOptionsMonitor` — singleton, всегда возвращает актуальное значение и уведомляет об изменениях.

> [!question]- Зачем ValidateOnStart?
> Чтобы ошибки конфигурации приводили к падению при запуске (fail fast), а не в рантайме.

> [!question]- Как использовать IOptionsSnapshot в singleton?
> Нельзя напрямую; используйте `IOptionsMonitor` либо создавайте scope.

## Связанные темы

- [[N:3ea33104867981bf8a02c3a4b52c7ec7]]
- [[N:3ea33104867981a6a9f0dc668b236e7a]]
