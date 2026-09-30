---
type: topic
domain: backend
stage: 1
section: "1.5"
order: 2
status: todo
level: junior
notion_id: 3ea331048679815d9264f038e53fd95e
tags: [domain/backend, stage/1, level/junior, topic/collections, topic/interfaces, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Интерфейсы коллекций: IEnumerable, ICollection, IList, IReadOnly

↑ [[BE 1.5 Коллекции и основы LINQ|1.5 Коллекции и основы LINQ]] · ← [[BE 1.5.1 Массивы, List, Dictionary, HashSet, Queue, Stack|Предыдущая]] · → [[BE 1.5.3 Generics — обобщённые типы и методы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->



































> [!info] Зачем это на собесе
> Что принимать и что возвращать из методов: `IEnumerable<T>`, `IReadOnlyList<T>`, `List<T>`? Это вопрос про дизайн API и про отложенное выполнение. Заодно проверяют, понимаете ли вы, что скрывается за `foreach` и `yield`.

> [!note] Переписано
> В Notion эта страница содержала шаблонный текст без отношения к теме. Здесь — содержательная версия.

## Объяснение

### Иерархия интерфейсов
| Интерфейс | Что добавляет | Изменяемая |
|---|---|---|
| `IEnumerable<T>` | перебор (`foreach`) | — |
| `IReadOnlyCollection<T>` | `Count` | нет |
| `IReadOnlyList<T>` | индексатор `[i]` | нет |
| `ICollection<T>` | `Count`, `Add`, `Remove`, `Clear`, `Contains` | да |
| `IList<T>` | индексатор, `Insert`, `RemoveAt` | да |
| `ISet<T>` | операции над множествами (`HashSet<T>`) | да |
| `IReadOnlyDictionary<K,V>` / `IDictionary<K,V>` | доступ по ключу | нет / да |

Все они наследуют `IEnumerable<T>`: `IReadOnlyList<T>` строится на `IReadOnlyCollection<T>`, `IList<T>` на `ICollection<T>`.


### `IEnumerable<T>`
Минимальный контракт «последовательность»: `GetEnumerator()` возвращает перечислитель с `MoveNext()` и `Current`. `foreach` разворачивается именно в него.
```csharp
foreach (var p in patients) { }
// эквивалентно:
using var e = patients.GetEnumerator();
while (e.MoveNext()) { var p = e.Current; }
```
- Последовательность может быть **ленивой** и даже бесконечной: элементы вычисляются по мере перебора.
- Многократное перечисление ленивой последовательности повторяет вычисление (запрос в БД, чтение файла) заново.
```csharp
IEnumerable<int> Evens()               // итератор: yield
{
    for (var i = 0; ; i += 2) yield return i;
}
var firstTen = Evens().Take(10).ToList();
```

### `ICollection<T>` и `IList<T>`
Изменяемые коллекции: добавление, удаление, `Count`. `IList<T>` добавляет доступ по индексу. Реализуют `List<T>`, массив (частично), `Collection<T>`.

### `IReadOnlyCollection<T>` и `IReadOnlyList<T>`
Только чтение: `Count` и индексатор, без методов изменения. **Не гарантируют неизменяемость** самих данных: под интерфейсом может быть обычный `List<T>`, который кто-то изменит.
```csharp
public sealed class Patient
{
    private readonly List<Encounter> _encounters = [];
    public IReadOnlyList<Encounter> Encounters => _encounters;   // наружу — только чтение
}
```
Для настоящей неизменяемости — `ImmutableArray<T>`, `ImmutableList<T>`, `FrozenSet<T>`/`FrozenDictionary<K,V>` (.NET 8).

### Что принимать и что возвращать
- **Параметры:** самый общий подходящий тип. Нужен только перебор — `IEnumerable<T>` (или `IReadOnlyCollection<T>`, если нужен `Count`). Нужен доступ по индексу — `IReadOnlyList<T>`.
- **Возвращаемые значения:** достаточно конкретный тип, чтобы вызывающий не пересчитывал. Готовый результат — `IReadOnlyList<T>` (или `T[]`, `List<T>` для внутренних API). Ленивый поток — `IEnumerable<T>` с явной документацией.
- Не отдавайте наружу внутренний `List<T>` и не принимайте `List<T>`, если хватает интерфейса.
```csharp
public IReadOnlyList<PatientDto> GetAll() => _repo.Query().Select(Map).ToList();   // материализован
public IEnumerable<PatientDto> Stream() => _repo.Query().Select(Map);               // ленивый, ответственность на вызывающем
```

### `IQueryable<T>`
Наследует `IEnumerable<T>`, но хранит **выражение** запроса (дерево `Expression`), которое провайдер (EF Core) транслирует в SQL. Пока не вызван `ToList`/`First`/`foreach`, запрос не выполняется. Смешение `IQueryable` и `IEnumerable` определяет, где выполнится фильтрация: в БД или в памяти.

### Ковариантность
`IEnumerable<out T>` и `IReadOnlyList<out T>` — ковариантны: `IEnumerable<Dog>` присваивается `IEnumerable<Animal>`. `List<T>` и `IList<T>` — инвариантны: `List<Dog>` нельзя присвоить `List<Animal>`, иначе можно было бы добавить туда `Cat`.

## Нюансы и подводные камни
- Возврат `IEnumerable<T>` из метода, который внутри держит `using`/соединение: перебор случится после закрытия ресурса. Материализуйте перед выходом или используйте `yield` внутри `using` осознанно.
- `IEnumerable<T>.Count()` перебирает всё, если нельзя определить размер быстро (LINQ проверяет `ICollection<T>`/`IReadOnlyCollection<T>`, но не всегда).
- Двойной перебор `IEnumerable` с запросом к БД или дорогим вычислением: выполнится дважды. Анализатор предупреждает (CA1851).
- `IReadOnlyList<T>` над `List<T>` — «представление», не копия: изменения отражаются.
- Приведение `IEnumerable<T>` к `List<T>` через `(List<T>)` работает, только если внутри действительно `List<T>`; используйте `ToList()`.

## Практика
- Переписать метод, принимающий `List<int>`, чтобы он принимал `IEnumerable<int>` и не перечислял дважды.
- Написать итератор с `yield`, который читает большой файл построчно.
- Показать разницу между ленивым и материализованным результатом на счётчике вызовов.

## Вопросы с ответами
> [!question]- Чем `IEnumerable<T>` отличается от `ICollection<T>` и `IList<T>`?
> `IEnumerable<T>` только перебор. `ICollection<T>` добавляет `Count` и изменение (`Add`, `Remove`). `IList<T>` дополнительно даёт доступ по индексу и вставку по позиции.

> [!question]- Что вернуть из метода: `List<T>`, `IEnumerable<T>` или `IReadOnlyList<T>`?
> Для готового результата `IReadOnlyList<T>`: вызывающий видит размер и индексы, но не может изменить внутреннее состояние. `IEnumerable<T>` — если поток ленивый.

> [!question]- Что такое отложенное выполнение и чем оно опасно?
> Вычисление происходит при переборе, а не при создании запроса. Опасности: повторный перебор пересчитывает, данные могут измениться между созданием и перебором, ресурс (соединение) может быть уже закрыт.

> [!question]- Чем `IQueryable<T>` отличается от `IEnumerable<T>`?
> `IQueryable` хранит выражение и транслируется провайдером (например, в SQL), `IEnumerable` — делегаты, выполняемые в памяти.

> [!question]- Почему `List<Dog>` нельзя присвоить `List<Animal>`, а `IEnumerable<Dog>` в `IEnumerable<Animal>` можно?
> `List<T>` изменяем и потому инвариантен (иначе можно было бы добавить Cat). `IEnumerable<out T>` только отдаёт элементы, поэтому ковариантен.

## Связанные темы
- Предыдущая: [[N:3ea331048679812fa686df688569debd]] · Следующая: [[N:3ea3310486798119a28cdce7837acb7f]]
- LINQ: [[N:3ea33104867981b1aae2edc717e3332c]]
- Ковариантность и generics глубоко: [[N:3ea33104867981d085d7ec58153f8c7b]]
- IQueryable и EF Core: [[N:3ea33104867981eaa401fe6bf019677c]]
