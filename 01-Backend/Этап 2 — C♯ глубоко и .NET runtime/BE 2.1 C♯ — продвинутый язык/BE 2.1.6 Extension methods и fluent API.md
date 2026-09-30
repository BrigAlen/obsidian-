---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 6
status: todo
level: middle
notion_id: 3ea33104867981efbe4bdf7ca565e0e1
tags: [domain/backend, stage/2, level/middle, topic/extensions, topic/fluent, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Extension methods и fluent API

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.5 Generics глубоко — constraints, вариантность, static abstract|Предыдущая]] · → [[BE 2.1.7 Records, init, with, required, primary constructors|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

























































> [!info] Зачем это на собесе
> extension-методы — основа LINQ и всей конфигурации ASP.NET Core (`services.AddXxx()`, `app.UseXxx()`). В проекте общие пакеты (`core/extensions`, `http_shared/DI`) подключаются именно так.

## Объяснение

Extension-метод — **статический** метод в **статическом** классе, первый параметр помечен `this`. Вызывается как метод экземпляра.
```csharp
public static class StringExtensions
{
    public static string? NullIfEmpty(this string? s) => string.IsNullOrWhiteSpace(s) ? null : s.Trim();
    public static string Truncate(this string s, int max) => s.Length <= max ? s : s[..max] + "…";
}

var middle = dto.MiddleName.NullIfEmpty();   // компилятор превращает в StringExtensions.NullIfEmpty(dto.MiddleName)
```
- Не имеют доступа к `private`-членам типа, только к публичному API.
- Не переопределяют методы: если у типа есть метод с той же сигнатурой, вызовется **метод экземпляра**.
- Разрешаются статически по типу переменной и подключённым `using`.
- Можно вызвать на `null` (это обычный статический вызов), поэтому проверяйте аргумент.

### Расширения для DI и pipeline (главный практический кейс)

```csharp
// пакет core/http_shared — одна строка подключения во всех сервисах
public static class HttpSharedExtensions
{
    public static IServiceCollection AddHttpShared(this IServiceCollection services, IConfiguration cfg)
    {
        services.AddHttpContextAccessor();
        services.AddScoped<IUserContext, UserContext>();
        services.AddExceptionHandler<GlobalExceptionHandler>();
        services.AddProblemDetails();
        services.Configure<KeycloakOptions>(cfg.GetSection("Keycloak"));
        return services;                              // возвращаем для цепочки (fluent)
    }

    public static IApplicationBuilder UseHttpShared(this IApplicationBuilder app) =>
        app.UseExceptionHandler().UseMiddleware<CorrelationIdMiddleware>();
}

// Program.cs сервиса
builder.Services.AddHttpShared(builder.Configuration).AddTracing(builder.Configuration);
app.UseHttpShared();
```

### Расширения для интерфейсов и generic

```csharp
public static class QueryableExtensions
{
    public static IQueryable<T> Page<T>(this IQueryable<T> q, int page, int size) =>
        q.Skip((page - 1) * size).Take(size);

    public static IQueryable<T> WhereIf<T>(this IQueryable<T> q, bool condition, Expression<Func<T, bool>> pred) =>
        condition ? q.Where(pred) : q;
}

var result = await db.Patients
    .WhereIf(filter.City is not null, p => p.City == filter.City)
    .OrderBy(p => p.LastName)
    .Page(filter.Page, 50)
    .ToListAsync(ct);
```

### Fluent API

Цепочка вызовов, где каждый метод возвращает объект для продолжения: `builder.Services.AddX().AddY()`, EF Core `modelBuilder.Entity<T>().HasKey(...).HasIndex(...)`, FluentValidation `RuleFor(x => x.Name).NotEmpty().MaximumLength(100)`, построители отчётов.

### C# 14: extension members

Новый синтаксис блоков `extension(Type t) { ... }` — можно объявлять extension-**свойства** и статические члены, а не только методы.

## Нюансы и подводные камни

- Экстеншены на `object` или `string` засоряют IntelliSense по всему проекту. Держите их в узких namespace.
- Бизнес-логика в extension-методах плохо тестируется и прячется от DI. Место экстеншенов — утилиты и конфигурация.
- Конфликт имён двух экстеншенов из разных `using` → ошибка неоднозначности.
- Extension-метод над `IEnumerable<T>` и `IQueryable<T>` с одинаковым именем: выбор зависит от статического типа. Легко случайно уйти в память.

## Тестирование

```csharp
[Theory]
[InlineData("  ", null)]
[InlineData(" Иван ", "Иван")]
public void NullIfEmpty_normalizes(string input, string? expected) =>
    input.NullIfEmpty().Should().Be(expected);
```

## Вопросы с ответами

> [!question]- Что такое extension-метод и как он работает?
> Статический метод статического класса с this у первого параметра. Компилятор превращает вызов obj.Method() в Class.Method(obj). Доступа к приватным членам нет.

> [!question]- Что вызовется, если у типа есть метод с такой же сигнатурой, как у extension-метода?
> Метод экземпляра: он имеет приоритет. Extension-метод используется, только если подходящего метода экземпляра нет.

> [!question]- Можно ли вызвать extension-метод на null?
> Да, это обычный статический вызов, и исключения при вызове не будет. Поэтому внутри нужно проверять аргумент.

> [!question]- Как организовать подключение общей библиотеки в десятках микросервисов?
> Extension-методы AddXxx для IServiceCollection и UseXxx для IApplicationBuilder в общем пакете. Сервис подключает всё одной строкой, а конфигурация и регистрация инкапсулированы в библиотеке.

## Связанные темы

- Предыдущая: [[N:3ea33104867981d085d7ec58153f8c7b]] · Следующая: [[N:3ea331048679810e866fff73c25c9cd8]]
- Организация регистраций в DI: [[N:3ea3310486798126917dc3763b7b5959]]
- LINQ глубоко: [[N:3ea33104867981dc98c9f760e86a24d5]]
- Общий код между сервисами: [[N:3ea3310486798108a3caf17276ee36aa]]
- Паттерн Builder: [[N:3ea33104867981b19175c65aa63799ff]]
