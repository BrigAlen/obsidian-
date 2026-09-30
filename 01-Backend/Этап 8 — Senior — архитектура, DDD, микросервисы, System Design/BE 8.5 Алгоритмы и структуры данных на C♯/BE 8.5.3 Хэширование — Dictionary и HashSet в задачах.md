---
type: topic
domain: backend
stage: 8
section: "8.5"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981c79650f64aae90de85
tags: [domain/backend, stage/8, level/senior, topic/algorithms, topic/hashing, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Хэширование: Dictionary и HashSet в задачах

↑ [[BE 8.5 Алгоритмы и структуры данных на C♯|8.5 Алгоритмы и структуры данных на C♯]] · ← [[BE 8.5.2 Массивы и строки — два указателя, скользящее окно|Предыдущая]] · → [[BE 8.5.4 Деревья, графы, BFS и DFS|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Хэш-таблица — самый частый способ снизить сложность до O(n).

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Типовые паттерны:

| Паттерн | Идея | Пример |
|---|---|---|
| Поиск дополнения | хранить уже виденное | Two Sum: `target - x` в словаре |
| Подсчёт частот | `Dictionary<T,int>` | анаграммы, top-k |
| Уникальность | `HashSet<T>` | дубликаты, пересечения |
| Группировка по ключу | `Dictionary<K, List<V>>` | группа анаграмм (ключ — отсортированная строка) |
| Префиксные суммы + словарь | количество подмассивов с суммой k | |
| Кэш результатов | мемоизация | |

```csharp
// Two Sum: O(n)
static int[]? TwoSum(int[] a, int target)
{
    var seen = new Dictionary<int, int>();
    for (int i = 0; i < a.Length; i++)
    {
        if (seen.TryGetValue(target - a[i], out var j)) return [j, i];
        seen[a[i]] = i;
    }
    return null;
}

// Количество подмассивов с суммой k
static int SubarraySum(int[] a, int k)
{
    var count = new Dictionary<int, int> { [0] = 1 };
    int sum = 0, res = 0;
    foreach (var x in a) { sum += x; res += count.GetValueOrDefault(sum - k); count[sum] = count.GetValueOrDefault(sum) + 1; }
    return res;
}

// Группировка анаграмм
static IList<IList<string>> Group(string[] words) =>
    words.GroupBy(w => new string(w.OrderBy(c => c).ToArray())).Select(g => (IList<string>)g.ToList()).ToList();
```

Как работает `Dictionary`: массив корзин, индекс = `hash(key) % size`; коллизии — цепочки/открытая адресация; при заполнении — перехеширование. Для собственных ключей переопределяют `Equals` и `GetHashCode` (или `record`).

## Нюансы и подводные камни

- Изменяемые поля в ключе после добавления ломают поиск.
- Худший случай O(n) при массовых коллизиях (в .NET есть рандомизация хэша строк).
- `HashSet` не гарантирует порядок.
- Память: словарь занимает больше, чем массив.
- Для порядка ключей — `SortedDictionary`.

## Практика

1. Решите: Two Sum, Valid Anagram, Group Anagrams, Longest Consecutive Sequence.
2. Реализуйте LRU-кэш на `Dictionary` + `LinkedList` (O(1)).
3. Напишите свой `GetHashCode` для составного ключа через `HashCode.Combine`.

## Вопросы с ответами

> [!question]- Как работает хэш-таблица?
> Хэш ключа определяет корзину; коллизии разрешаются цепочками или адресацией; при росте выполняется перехеширование.

> [!question]- Что нужно для собственного типа-ключа?
> Согласованные `Equals` и `GetHashCode`, неизменяемые поля ключа.

## Связанные темы

- [[N:3ea331048679819daa86c3ba7f89d3c4]]
- [[N:3ea33104867981f2bab1ca488af03764]]
