---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 9
status: todo
level: middle
notion_id: 3ea331048679819dabaffeca732fabc4
tags: [domain/backend, stage/2, level/middle, topic/reflection, topic/attributes, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Атрибуты и рефлексия

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.8 Span и Memory — stackalloc, ref struct|Предыдущая]] · → [[BE 2.1.10 Source generators и Roslyn (как в analytics_generator)|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


































> [!info] Зачем это на собесе
> Рефлексия стоит за DI, ORM, сериализацией и тестовыми фреймворками. Спросят, что такое атрибут и как его прочитать, чем рефлексия плоха для производительности и AOT, чем её можно заменить (expression trees, source generators) и как написать собственный атрибут.

> [!note] Переписано
> В Notion эта страница содержала шаблонный текст без отношения к теме. Здесь — содержательная версия.

## Объяснение

### Атрибуты
Декларативные метаданные, прикрепляемые к сборке, типу, члену, параметру. Сами по себе ничего не делают: их читает компилятор, среда выполнения или ваш код через рефлексию.
```csharp
[Obsolete("Используйте NewApi", error: false)]
public void OldApi() { }

[Serializable]
[JsonPropertyName("last_name")]
public string LastName { get; set; } = "";

[HttpGet("{id:guid}"), Authorize(Roles = "Doctor")]      // атрибуты ASP.NET Core
public IActionResult Get(Guid id) => ...;
```
Собственный атрибут:
```csharp
[AttributeUsage(AttributeTargets.Property, AllowMultiple = false, Inherited = true)]
public sealed class ExportColumnAttribute(string title, int order = 0) : Attribute
{
    public string Title { get; } = title;
    public int Order { get; } = order;
}

public class PatientRow
{
    [ExportColumn("ФИО", 1)] public string FullName { get; set; } = "";
    [ExportColumn("Возраст", 2)] public int Age { get; set; }
}
```
Соглашение: имя класса заканчивается на `Attribute`, при использовании суффикс можно опустить.

### Рефлексия
Доступ к метаданным типов во время выполнения: получить тип, его члены, значения, создать объект, вызвать метод.
```csharp
var type = typeof(PatientRow);                              // или obj.GetType()
var props = type.GetProperties(BindingFlags.Public | BindingFlags.Instance);
foreach (var p in props)
{
    var attr = p.GetCustomAttribute<ExportColumnAttribute>();   // читаем атрибут
    if (attr is not null) Console.WriteLine($"{attr.Order}: {attr.Title} = {p.GetValue(row)}");
}

var obj = Activator.CreateInstance(type);                       // создать экземпляр
type.GetMethod("Calculate")!.Invoke(obj, new object[] { 42 }); // вызвать метод
var closed = typeof(List<>).MakeGenericType(typeof(int));       // построить закрытый generic
```
Типовые применения: DI-контейнеры (поиск конструкторов), ORM (маппинг свойств), сериализаторы, валидаторы (`[Required]`), тестовые фреймворки (`[Fact]`), плагины (загрузка сборок через `Assembly.Load` и поиск реализаций интерфейса).

### Цена рефлексии
- Медленнее прямого вызова в десятки раз (поиск метаданных, проверки доступа, боксинг аргументов).
- Не работает надёжно с **trimming** и **Native AOT**: компилятор не видит, какие члены вызываются динамически, и может их удалить.
- Ломается при переименованиях: строки с именами членов не проверяются компилятором (`nameof` частично помогает).
- Нарушает инкапсуляцию: через рефлексию доступны `private` члены.

### Как ускорить и чем заменить
- **Кэшировать** `PropertyInfo`/`MethodInfo`, а не искать их в каждом вызове.
- **Скомпилированные делегаты:** `Delegate.CreateDelegate` или **Expression trees** (`Expression.Lambda(...).Compile()`) — один раз построить и вызывать как обычный делегат.
- **Source generators**: генерация кода на этапе компиляции вместо рефлексии (System.Text.Json source generation, `[LoggerMessage]`, `[GeneratedRegex]`).
- `typeof(T)` и generics с ограничениями вместо `GetType()` там, где тип известен.
- Атрибуты `[DynamicallyAccessedMembers]` подсказывают тримингу, что нужно сохранить.

### Полезные шаблоны
```csharp
// найти все реализации интерфейса в сборке (регистрация обработчиков)
var handlers = typeof(IHandler).Assembly.GetTypes()
    .Where(t => t is { IsAbstract: false, IsInterface: false } && typeof(IHandler).IsAssignableFrom(t));

// проверить наличие атрибута
bool isAudited = type.IsDefined(typeof(AuditedAttribute), inherit: true);
```

## Нюансы и подводные камни
- `GetProperties()` без `BindingFlags` возвращает только публичные экземплярные члены; закрытые нужны явно.
- `Invoke` оборачивает исключения метода в `TargetInvocationException` — смотрите `InnerException`.
- Рефлексия по `private`-члену чужой библиотеки ломается при обновлении версии.
- Значения аргументов атрибута — константы времени компиляции: нельзя передать произвольный объект или лямбду.
- `Type.GetType("Namespace.Class")` требует имя с сборкой для типов из других сборок.
- Чтение атрибутов в горячем пути без кэша заметно замедляет приложение.

## Практика
- Написать экспортёр в CSV, который строит колонки по атрибутам свойств; замерить скорость и ускорить кэшированием и скомпилированными делегатами.
- Найти через рефлексию все классы, помеченные вашим атрибутом, и зарегистрировать их в DI.
- Сравнить вызов метода напрямую, через `Invoke` и через скомпилированный `Expression` в BenchmarkDotNet.

## Вопросы с ответами
> [!question]- Что такое атрибут и как он работает?
> Метаданные, прикреплённые к элементу кода. Сами по себе не выполняют логику: их читает компилятор, среда выполнения или код через рефлексию.

> [!question]- Почему рефлексия медленная и как её ускорить?
> Поиск метаданных, проверки безопасности и боксинг на каждом вызове. Ускорение: кэшировать `MethodInfo`/`PropertyInfo`, создавать делегаты или скомпилированные выражения, использовать source generators.

> [!question]- Почему рефлексия проблемна для Native AOT и trimming?
> Компилятор статически определяет используемый код. Члены, к которым обращаются только по имени в рантайме, он может удалить как неиспользуемые. Нужны аннотации `DynamicallyAccessedMembers` или генерация кода.

> [!question]- Как прочитать значение атрибута?
> `member.GetCustomAttribute<MyAttribute>()` возвращает экземпляр с заданными значениями, либо `null`. `IsDefined` проверяет только наличие.

> [!question]- Что вернёт `Invoke`, если метод бросил исключение?
> `TargetInvocationException`, а исходное исключение лежит в `InnerException`.

## Связанные темы
- Предыдущая: [[N:3ea33104867981548d57ffd75d21ec61]] · Следующая: [[N:3ea331048679816ca016dc47df98b9ec]]
- Деревья выражений: [[N:3ea33104867981dc98c9f760e86a24d5]]
- Source generators: [[N:3ea331048679816ca016dc47df98b9ec]]
- Сериализация: [[N:3ea331048679818ea358eaece94428c4]]
- DI и рефлексия: [[N:3ea33104867981c998bfcabbb5f926bd]]
