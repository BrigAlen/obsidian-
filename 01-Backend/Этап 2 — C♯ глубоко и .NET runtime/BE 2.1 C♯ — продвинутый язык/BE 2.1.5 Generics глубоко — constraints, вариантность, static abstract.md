---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981d085d7ec58153f8c7b
tags: [domain/backend, stage/2, level/middle, topic/generics, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Generics глубоко: constraints, вариантность, static abstract

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.4 yield, итераторы, IAsyncEnumerable|Предыдущая]] · → [[BE 2.1.6 Extension methods и fluent API|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




















> [!info] Зачем это на собесе
> Senior-вопросы про generics: чем ковариантность отличается от контравариантности, почему `List<Dog>` нельзя присвоить `List<Animal>`, что такое `static abstract` в интерфейсах и generic math, как CLR разделяет код для значимых и ссылочных типов.

> [!note] Переписано
> В Notion эта страница содержала шаблонный текст без отношения к теме. Здесь — содержательная версия.

## Объяснение

### Ограничения: что ещё умеет `where`
```csharp
public static T Max<T>(T a, T b) where T : IComparable<T> => a.CompareTo(b) >= 0 ? a : b;

public class Repo<T> where T : class, IEntity, new() { }             // комбинация: class + интерфейс + new()
public static T Parse<T>(string s) where T : IParsable<T> => T.Parse(s, null);   // C# 11: статический интерфейсный член
public static void Fill<T>(Span<T> span) where T : unmanaged { }     // без ссылок: можно stackalloc, работа с байтами
public ref struct Reader<T> where T : allows ref struct { }          // C# 13: разрешить ref struct как аргумент типа
```
- Ограничение `default` — уточняет перегрузки для `T?` в переопределениях.
- `where T : notnull` — запрет `null`, полезно для ключей.

### Вариантность
Вариантность — можно ли использовать `Generic<Derived>` там, где ожидается `Generic<Base>`.
- **Ковариантность (`out T`)**: тип только **отдаёт** T (результат, возвращаемое значение). `IEnumerable<out T>`, `IReadOnlyList<out T>`, `Func<out TResult>`.
```csharp
IEnumerable<Dog> dogs = GetDogs();
IEnumerable<Animal> animals = dogs;          // можно: из IEnumerable<Animal> мы только читаем
```
- **Контравариантность (`in T`)**: тип только **принимает** T (параметр). `IComparer<in T>`, `Action<in T>`, `IEqualityComparer<in T>`.
```csharp
Action<Animal> feedAnimal = a => Feed(a);
Action<Dog> feedDog = feedAnimal;            // можно: обработчик для любых животных подойдёт для собак
```
- **Инвариантность** — по умолчанию: `List<T>`, `IList<T>`, `Dictionary<K,V>` (изменяемые, T и на вход, и на выход).
```csharp
List<Animal> a = new List<Dog>();            // ошибка: иначе a.Add(new Cat()) сломало бы список собак
```
Объявление вариантности своих интерфейсов:
```csharp
public interface IProducer<out T> { T Produce(); }
public interface IConsumer<in T> { void Consume(T item); }
```
Работает только для **интерфейсов и делегатов** и только для **ссылочных типов** в аргументе (`IEnumerable<int>` в `IEnumerable<object>` нельзя: потребовался бы boxing).
Массивы ковариантны исторически (`object[] o = new string[1]`), что даёт исключение `ArrayTypeMismatchException` при записи неверного типа.

### `static abstract` и generic math (C# 11, .NET 7)
Интерфейс может требовать статические члены и операторы:
```csharp
public interface IShape<TSelf> where TSelf : IShape<TSelf>
{
    static abstract TSelf Create(double size);
    static abstract double Area(TSelf shape);
}

public static T Sum<T>(IEnumerable<T> items) where T : INumber<T>
{
    T total = T.Zero;
    foreach (var x in items) total += x;      // оператор + через интерфейс INumber<T>
    return total;
}
var s1 = Sum([1, 2, 3]);         // int
var s2 = Sum([1.5, 2.5]);        // double
```
Раньше для этого приходилось дублировать код под каждый числовой тип или использовать `dynamic`.

### Как CLR исполняет generics
- Для каждого **значимого типа** в аргументе JIT создаёт **отдельный** нативный код (`List<int>`, `List<double>`): без boxing, максимальная скорость.
- Для **ссылочных типов** код **общий** (`__Canon`): все ссылки одного размера, поэтому один код на все.
- Информация о типе сохраняется в рантайме (реификация), в отличие от стирания в Java.
```csharp
typeof(List<int>) != typeof(List<string>)             // разные закрытые типы
typeof(List<>)                                         // открытый generic тип
typeof(List<>).MakeGenericType(typeof(int))           // построение закрытого типа в рантайме
```

### Generics и DI
```csharp
services.AddScoped(typeof(IRepository<>), typeof(Repository<>));   // открытый generic: любой IRepository<T>
services.AddTransient(typeof(IValidator<>), typeof(DefaultValidator<>));
```

### Полезные приёмы
- **CRTP** (`where TSelf : Base<TSelf>`) — базовый класс знает конкретный тип наследника, например для fluent-билдеров.
- Generic-атрибуты (C# 11): `[JsonConverter<T>]` вместо `typeof`.
- Статический generic-класс как кэш: `static class Cache<T> { public static readonly Func<T> Factory = ...; }` — у каждого T свои статические поля.

## Нюансы и подводные камни
- `IEnumerable<Dog>` в `IEnumerable<Animal>` — можно, `List<Dog>` в `List<Animal>` — нельзя: смешивают ковариантность интерфейса и инвариантность класса.
- Вариантность для значимых типов не работает: `IEnumerable<int>` не станет `IEnumerable<object>`.
- Сравнение `T` через `==` недоступно без ограничения. Используйте `EqualityComparer<T>.Default`.
- Открытые generic-регистрации в DI не поддерживают ограничения без явной проверки: при несоответствии получите исключение при разрешении.
- Чрезмерно абстрактные generic-иерархии тяжело читать; generics нужны для реального переиспользования, а не «на всякий случай».

## Практика
- Написать `Result<T>` с ковариантным интерфейсом `IResult<out T>`.
- Реализовать `Sum` и `Average` для `INumber<T>` и сравнить скорость с версией под `int`.
- Объяснить, почему `Action<Dog>` нельзя присвоить `Action<Animal>`.

## Вопросы с ответами
> [!question]- Чем ковариантность отличается от контравариантности?
> Ковариантность (`out`): `Generic<Derived>` можно использовать как `Generic<Base>`, когда тип только отдаёт значения. Контравариантность (`in`): `Generic<Base>` подходит как `Generic<Derived>`, когда тип только принимает значения.

> [!question]- Почему `List<Dog>` нельзя присвоить `List<Animal>`?
> `List<T>` и читает, и записывает T. Иначе через ссылку `List<Animal>` в список собак можно было бы добавить кошку, что нарушило бы типобезопасность.

> [!question]- Зачем нужны `static abstract` члены интерфейсов?
> Чтобы обобщённый код мог вызывать статические члены и операторы типа-аргумента (`T.Zero`, `a + b`). На этом построен generic math (`INumber<T>`).

> [!question]- Как работают generics в CLR для значимых и ссылочных типов?
> Для каждого значимого типа JIT создаёт отдельную версию кода. Для ссылочных используется общий код. Информация о типах сохраняется в рантайме.

> [!question]- Что такое открытый generic-тип и где он нужен?
> Тип с неуказанным аргументом (`List<>`). Используется в DI (`typeof(IRepository<>)`), рефлексии и при построении типов в рантайме.

## Связанные темы
- Предыдущая: [[N:3ea3310486798160917dfb8938b23233]] · Следующая: [[N:3ea33104867981efbe4bdf7ca565e0e1]]
- Generics основы: [[N:3ea3310486798119a28cdce7837acb7f]]
- Интерфейсы: [[N:3ea33104867981058510f56e083959bd]]
- DI: [[N:3ea33104867981c998bfcabbb5f926bd]]
- Generics в TypeScript: [[N:3ea331048679812d9621f339f8175cdd]]
