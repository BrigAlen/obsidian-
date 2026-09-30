---
type: topic
domain: backend
stage: 3
section: "3.2"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981d2bc3bc47bf945c910
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/di, topic/pitfalls, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Captive dependency и другие ловушки DI

↑ [[BE 3.2 Dependency Injection|3.2 Dependency Injection]] · ← [[BE 3.2.2 Время жизни — Singleton, Scoped, Transient|Предыдущая]] · → [[BE 3.2.4 Keyed services, фабрики, декораторы, IServiceScopeFactory|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
































> [!info] Зачем это на собесе
> «Найдите баг в регистрации» — типичная задача на ревью кода. Captive dependency — самая известная ловушка.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Captive dependency** — долгоживущий сервис держит ссылку на короткоживущий, продлевая ему жизнь.

```csharp
builder.Services.AddSingleton<ReportCache>();   // singleton
builder.Services.AddScoped<AppDbContext>();      // scoped

public class ReportCache(AppDbContext db) { }   // db «застрял» в singleton: один DbContext на всё приложение, гонки и устаревший кэш
```

Исправление: зависеть от `IServiceScopeFactory` / `IDbContextFactory<T>` и создавать scope на операцию.

```csharp
public class ReportCache(IServiceScopeFactory scopes)
{
    public async Task<Report> LoadAsync(int id)
    {
        using var scope = scopes.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        return await db.Reports.FindAsync(id);
    }
}
```

### Другие ловушки

| Ловушка | Последствие | Как избежать |
|---|---|---|
| Service Locator | скрытые зависимости, сложные тесты | внедрять через конструктор |
| Transient `IDisposable` в корневом контейнере | утечка памяти | Scoped или создавать вручную |
| Блокирующая логика в конструкторе | медленный запрос, deadlock | выносить в `InitializeAsync` |
| Циклические зависимости | исключение | выделить третий сервис или события |
| Разрешение из корня scoped-сервиса | исключение с включённой валидацией | использовать scope |
| Тяжёлый граф на запрос | лишние аллокации | пересмотреть время жизни |
| `new` внутри сервиса вместо DI | нельзя заменить в тестах | внедрить зависимость |

### Инструменты

`ServiceProviderOptions { ValidateScopes = true, ValidateOnBuild = true }` находит captive dependency и незарегистрированные зависимости при старте.

## Нюансы и подводные камни

- Валидация областей включена по умолчанию только в Development.
- Async-инициализация в конструкторе невозможна — используйте фабричные методы или hosted-service «прогрев».
- Registered `IEnumerable<T>` порядок зависит от порядка регистрации; последняя регистрация выигрывает при запросе одиночного `T`.

## Практика

1. Воспроизведите captive dependency и покажите, как её ловит `ValidateScopes`.
2. Перепишите singleton, используя `IDbContextFactory`.
3. Включите `ValidateOnBuild` на своём проекте.

## Вопросы с ответами

> [!question]- Что такое captive dependency?
> Ситуация, когда сервис с длинным временем жизни удерживает сервис с коротким, из-за чего тот живёт дольше, чем должен.

> [!question]- Как безопасно использовать scoped в singleton?
> Через `IServiceScopeFactory` (создать scope на операцию) или `IDbContextFactory` для EF.

> [!question]- Почему Service Locator — антипаттерн?
> Зависимости неявны, тесты и анализ кода усложняются, ошибки регистрации проявляются только в рантайме.

## Связанные темы

- [[N:3ea331048679815b938fd2f3f2a7c66d]]
- [[N:3ea331048679816788e0df486d1eca06]]
