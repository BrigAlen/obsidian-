---
type: topic
domain: backend
stage: 1
section: "1.5"
order: 4
status: todo
level: junior
notion_id: 3ea33104867981b1aae2edc717e3332c
tags: [domain/backend, stage/1, level/junior, topic/linq, priority/must]
reviewed:
next_review:
priority: must
time: 8
---

# LINQ: основные операторы

↑ [[BE 1.5 Коллекции и основы LINQ|1.5 Коллекции и основы LINQ]] · ← [[BE 1.5.3 Generics — обобщённые типы и методы|Предыдущая]] · → [[BE 1.5.5 Сложность операций с коллекциями и выбор структуры|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->




































































> [!info] Зачем это на собесе
> LINQ пишут ежедневно: фильтрация, группировка, агрегация данных для отчётов и API. На собесе дают коллекцию и просят написать запрос, и следят за эффективностью (N·M, лишние перечисления).

## Объяснение

LINQ — набор методов-расширений над `IEnumerable<T>` (и `IQueryable<T>`). Два синтаксиса: **методы** (используют чаще) и **query syntax** (как SQL).

### Основные операторы

```csharp
var patients = GetPatients();

// фильтрация и проекция
var names = patients.Where(p => p.Age >= 18).Select(p => $"{p.LastName} {p.FirstName}");

// сортировка
var sorted = patients.OrderBy(p => p.LastName).ThenByDescending(p => p.BirthDate);

// элементы
patients.First(p => p.Id == id);            // исключение, если нет
patients.FirstOrDefault(p => p.Id == id);   // null/default
patients.Single(p => p.Snils == snils);     // исключение, если 0 или больше 1 — проверка уникальности
patients.Last(); patients.ElementAt(3);

// кванторы
patients.Any(p => p.IsDeleted);             // есть ли хоть один — O(1)–O(n), лучше чем Count() > 0
patients.All(p => p.Age > 0);
patients.Contains(p);

// агрегаты
patients.Count(p => p.City == "Минск");
patients.Sum(p => p.Debt); patients.Average(p => p.Age); patients.Max(p => p.BirthDate);
patients.MaxBy(p => p.Age);                 // .NET 6: сам элемент, а не значение
patients.Aggregate(0m, (acc, p) => acc + p.Debt);

// группировка
var byCity = patients.GroupBy(p => p.City)
    .Select(g => new { City = g.Key, Count = g.Count(), AvgAge = g.Average(p => p.Age) });
var countByDay = visits.CountBy(v => v.Date);   // .NET 9

// соединения
var q = from e in encounters
        join p in patients on e.PatientId equals p.Id
        select new { p.LastName, e.Date };
var left = encounters.LeftJoin(patients, e => e.PatientId, p => p.Id, (e, p) => new { e, p });  // .NET 10; раньше GroupJoin + SelectMany + DefaultIfEmpty

// разворачивание
var allDiagnoses = encounters.SelectMany(e => e.Diagnoses);

// множества и уникальность
ids.Distinct(); patients.DistinctBy(p => p.Snils); a.Union(b); a.Intersect(b); a.Except(b);

// страницы и порции
patients.Skip(20).Take(10);
patients.Chunk(500);                        // батчи по 500 (для вставки в ClickHouse)

// преобразование
patients.ToList(); patients.ToArray(); patients.ToDictionary(p => p.Id); patients.ToLookup(p => p.City);
```

### Query syntax

```csharp
var result = from p in patients
             where p.Age >= 18
             orderby p.LastName
             group p by p.City into g
             select new { City = g.Key, Count = g.Count() };
```
Удобен для сложных join и `let`. Компилятор превращает его в вызовы методов.

### Ленивые и немедленные операторы

- **Ленивые** (отложенное выполнение): `Where`, `Select`, `OrderBy`, `GroupBy`, `Skip`, `Take` — строят конвейер.
- **Немедленные:** `ToList`, `ToArray`, `ToDictionary`, `Count`, `Sum`, `First`, `Any`, `Max` — запускают перечисление.

## Нюансы и подводные камни

- `Count() > 0` вместо `Any()` — перебирает всё. `Any()` останавливается на первом.
- `Where(...).First()` = `First(predicate)` — пишите короче.
- `First` vs `Single`: `Single` проверяет уникальность и перебирает дальше. Используйте его, когда дубликат — ошибка данных.
- Вложенный `Where` или `Contains` по списку внутри `Select` — O(n·m). Строите `Dictionary` или `ToLookup` заранее.
- `OrderBy` стабилен, но O(n log n). Для топ-K без полной сортировки есть `MinBy`/`MaxBy` или `PriorityQueue`.
- В EF Core не все методы транслируются в SQL: при клиентской оценке EF бросает исключение, а не молча грузит таблицу (с EF Core 3).
- Замыкание на переменную цикла или изменяемое поле в отложенном запросе даст значение на момент выполнения, а не создания.

## Тестирование

```csharp
[Fact]
public void Groups_patients_by_city()
{
    var patients = new[] { P("Минск"), P("Минск"), P("Гродно") };
    var result = patients.GroupBy(p => p.City).ToDictionary(g => g.Key, g => g.Count());
    result.Should().BeEquivalentTo(new Dictionary<string, int> { ["Минск"] = 2, ["Гродно"] = 1 });
}
```

## Вопросы с ответами

> [!question]- Чем First отличается от Single и FirstOrDefault?
> First возвращает первый подходящий или бросает исключение, если нет ни одного. FirstOrDefault вместо исключения возвращает default. Single требует ровно один элемент, иначе исключение (ни одного или несколько).

> [!question]- Что такое отложенное выполнение в LINQ?
> Операторы вроде Where и Select не выполняются сразу, а строят конвейер. Он запускается при перечислении (foreach, ToList, Count), причём при каждом перечислении заново.

> [!question]- Как сделать left join в LINQ?
> GroupJoin + SelectMany + DefaultIfEmpty (или в query syntax: join … into g from x in g.DefaultIfEmpty()). В .NET 10 появился метод LeftJoin.

> [!question]- Как эффективно найти для каждого заказа его клиента в двух больших списках?
> Построить словарь клиентов по Id (ToDictionary) и искать за O(1), либо Join, который внутри использует хэш-таблицу. Не использовать First внутри Select — это O(n·m).

> [!question]- Чем GroupBy отличается от ToLookup?
> GroupBy отложенный и вычисляется при перечислении. ToLookup немедленно строит неизменяемую структуру «ключ → набор элементов» с быстрым доступом по ключу.

## Связанные темы

- Предыдущая: [[N:3ea3310486798119a28cdce7837acb7f]] · Следующая: [[N:3ea33104867981cb85d9fac53b3594f7]]
- LINQ глубоко: [[N:3ea33104867981dc98c9f760e86a24d5]]
- Интерфейсы коллекций: [[N:3ea331048679815d9264f038e53fd95e]]
- JOIN и GROUP BY в SQL: [[N:3ea33104867981bf8b23fa952e9bc832]]
- Методы массивов в JS: [[N:3ea33104867981f9b32fe932432f0651]]
