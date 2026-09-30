---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981dc98c9f760e86a24d5
tags: [domain/backend, stage/2, level/middle, topic/linq, topic/expressions, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# LINQ глубоко: отложенное выполнение, IEnumerable и IQueryable, expression trees

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.2 События и паттерн Observer в C♯|Предыдущая]] · → [[BE 2.1.4 yield, итераторы, IAsyncEnumerable|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





































> [!info] Зачем это на собесе
> senior-уровень LINQ: понимать отложенное выполнение, разницу `Func` и `Expression<Func>`, как EF Core превращает C# в SQL и почему иногда грузит всю таблицу. Это напрямую влияет на производительность сервисов.

## Объяснение

### Отложенное выполнение изнутри

LINQ to Objects построен на итераторах (`yield return`). Конвейер `Where → Select` не создаёт промежуточных списков: элементы проходят по одному при перечислении.
```csharp
static IEnumerable<T> MyWhere<T>(IEnumerable<T> source, Func<T, bool> predicate)
{
    foreach (var item in source)
        if (predicate(item)) yield return item;    // ленивая выдача
}

var query = patients.Where(p => { Console.Write("W "); return p.Age > 18; })
                    .Select(p => { Console.Write("S "); return p.Name; });
// ничего не выведено
foreach (var n in query) { }   // W S W W S ... — элементы идут по конвейеру по одному
```
- **Потоковые** операторы (`Where`, `Select`, `Take`) обрабатывают по одному элементу.
- **Буферизующие** (`OrderBy`, `GroupBy`, `Reverse`, `Distinct`) при первом запросе элемента читают весь источник.

### Func против Expression\<Func\>

```csharp
Func<Patient, bool> f = p => p.Age > 18;                    // скомпилированный делегат (IL-код)
Expression<Func<Patient, bool>> e = p => p.Age > 18;       // ДЕРЕВО ВЫРАЖЕНИЯ — данные, описывающие код
```
- `IEnumerable.Where(Func)` — выполняет делегат в памяти.
- `IQueryable.Where(Expression)` — передаёт дерево провайдеру, который **транслирует** его (EF Core → SQL, Hot Chocolate → запрос к источнику).
```csharp
// ОШИБКА: метод принимает Func — EF не видит условие, тянет всю таблицу и фильтрует в памяти
IEnumerable<Patient> Filter(Func<Patient, bool> pred) => db.Patients.Where(pred);

// ПРАВИЛЬНО: Expression — условие уходит в SQL WHERE
IQueryable<Patient> Filter(Expression<Func<Patient, bool>> pred) => db.Patients.Where(pred);
```

### Expression trees

Код как структура данных: можно анализировать, строить и компилировать в рантайме.
```csharp
Expression<Func<Patient, bool>> expr = p => p.City == "Минск";
var body = (BinaryExpression)expr.Body;       // Equal(Member(p.City), Constant("Минск"))

// динамический фильтр (например, из параметров GraphQL или UI-таблицы)
static Expression<Func<T, bool>> PropertyEquals<T>(string prop, object value)
{
    var p = Expression.Parameter(typeof(T), "x");
    var body = Expression.Equal(Expression.PropertyOrField(p, prop), Expression.Constant(value));
    return Expression.Lambda<Func<T, bool>>(body, p);
}
var q = db.Patients.Where(PropertyEquals<Patient>("City", "Минск"));

var compiled = expr.Compile();   // превратить в делегат (дорого — кэшируйте)
```
Где используются: ORM (EF Core, linq2db), GraphQL-фильтры и проекции (Hot Chocolate `[UseFiltering]`), маппинг (AutoMapper `ProjectTo`), спецификации, валидаторы (`RuleFor(x => x.Name)` в FluentValidation берёт имя свойства из выражения).

### Трансляция EF Core

- Только известные провайдеру конструкции: операторы, `Contains`, `StartsWith`, `EF.Functions.ILike`, агрегаты, навигационные свойства.
- Вызов вашего C#-метода внутри `Where` не транслируется → исключение (EF Core 3+).
- Финальный `Select` может выполнить часть на клиенте (проекция), но фильтры и сортировки должны быть транслируемы.

## Нюансы и подводные камни

- `AsEnumerable()` посреди запроса к EF переводит всё дальнейшее в память. Ставьте его осознанно, после фильтрации.
- `ToList()` внутри цикла или в проекции — N+1 запросов.
- `Compile()` дорогой (генерация IL): кэшируйте скомпилированные выражения.
- Захваченная в выражение переменная становится **параметром** SQL (хорошо для плана запроса). Константа в выражении — литералом.
- LINQ-запрос над изменяемой коллекцией, выполненный позже, видит изменения, внесённые после его создания.

## Тестирование

```csharp
[Fact]
public void Dynamic_filter_matches_property()
{
    var data = new[] { new Patient { City = "Минск" }, new Patient { City = "Брест" } }.AsQueryable();
    data.Where(PropertyEquals<Patient>("City", "Минск")).Should().ContainSingle();
}
```
Трансляцию запросов проверяйте интеграционными тестами на реальной БД (Testcontainers) и `ToQueryString()`:
```csharp
var sql = db.Patients.Where(p => p.City == "Минск").ToQueryString();
```

## Вопросы с ответами

> [!question]- Чем Func и Expression\<Func\> отличаются?
> Func — скомпилированный делегат, который можно только выполнить. Expression — дерево выражения, описывающее код как данные: его можно анализировать и транслировать в другой язык, например в SQL.

> [!question]- Почему запрос через EF Core может загрузить всю таблицу в память?
> Если в цепочке появился IEnumerable (AsEnumerable, метод с параметром Func вместо Expression, ToList до фильтра), дальнейшие операторы выполняются в памяти.

> [!question]- Какие LINQ-операторы потоковые, а какие буферизующие?
> Потоковые (Where, Select, Take, Skip) обрабатывают элементы по одному. Буферизующие (OrderBy, GroupBy, Distinct, Reverse) сначала читают весь источник.

> [!question]- Где применяются expression trees?
> ORM (EF Core), динамические фильтры и сортировки, GraphQL-фильтрация, AutoMapper ProjectTo, FluentValidation, построение быстрых геттеров вместо рефлексии.

> [!question]- Как увидеть SQL, который сгенерирует EF Core?
> ToQueryString(), логирование команд (LogTo, категория Microsoft.EntityFrameworkCore.Database.Command) или трассировка в OpenTelemetry.

## Связанные темы

- Предыдущая: [[N:3ea33104867981d5ae6bf41415020435]] · Следующая: [[N:3ea3310486798160917dfb8938b23233]]
- LINQ основы: [[N:3ea33104867981b1aae2edc717e3332c]]
- IEnumerable и IQueryable: [[N:3ea331048679815d9264f038e53fd95e]]
- Производительность EF Core: [[N:3ea3310486798111a4bafaf4f54018b5]]
- Hot Chocolate: фильтрация: [[N:3ea33104867981bf90d1f3ec3e986fe2]]
