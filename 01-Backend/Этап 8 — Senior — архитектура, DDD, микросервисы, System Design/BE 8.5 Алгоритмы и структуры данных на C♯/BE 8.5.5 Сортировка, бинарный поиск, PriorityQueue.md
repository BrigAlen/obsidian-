---
type: topic
domain: backend
stage: 8
section: "8.5"
order: 5
status: todo
level: senior
notion_id: 3ea3310486798163bed2e35a8324595b
tags: [domain/backend, stage/8, level/senior, topic/algorithms, topic/sorting, topic/search, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Сортировка, бинарный поиск, PriorityQueue

↑ [[BE 8.5 Алгоритмы и структуры данных на C♯|8.5 Алгоритмы и структуры данных на C♯]] · ← [[BE 8.5.4 Деревья, графы, BFS и DFS|Предыдущая]] · → [[BE 8.5.6 Динамическое программирование|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Знание сортировок, бинарного поиска (включая «по ответу») и кучи для top-k.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Сортировка | Средняя | Худшая | Память | Устойчивая |
|---|---|---|---|---|
| Quicksort | n log n | n² | log n | нет |
| Mergesort | n log n | n log n | n | да |
| Heapsort | n log n | n log n | 1 | нет |
| Insertion (малые n) | n² | n² | 1 | да |
| Counting/Radix | n + k | n + k | k | да |

В .NET `Array.Sort`/`List.Sort` — introsort (быстрая + heap + insertion), **неустойчива**; `OrderBy` в LINQ — устойчивая.

**Бинарный поиск** — O(log n) в отсортированной структуре или по монотонному условию.

```csharp
static int LowerBound(int[] a, int x)          // первый индекс, где a[i] >= x
{
    int lo = 0, hi = a.Length;
    while (lo < hi) { int mid = lo + (hi - lo) / 2; if (a[mid] < x) lo = mid + 1; else hi = mid; }
    return lo;
}

// Бинарный поиск «по ответу»: минимальная скорость поедания, чтобы успеть за h часов
static int MinSpeed(int[] piles, int h)
{
    int lo = 1, hi = piles.Max();
    while (lo < hi)
    {
        int mid = lo + (hi - lo) / 2;
        long hours = piles.Sum(p => (long)Math.Ceiling(p / (double)mid));
        if (hours <= h) hi = mid; else lo = mid + 1;
    }
    return lo;
}
```

**PriorityQueue\<TElement, TPriority>** (.NET 6+) — двоичная min-куча.

```csharp
// Top-K частых элементов: O(n log k)
static int[] TopK(int[] nums, int k)
{
    var pq = new PriorityQueue<int, int>();
    foreach (var (num, cnt) in nums.GroupBy(x => x).Select(g => (g.Key, g.Count())))
    {
        pq.Enqueue(num, cnt);
        if (pq.Count > k) pq.Dequeue();          // удаляем наименее частый
    }
    return pq.UnorderedItems.Select(x => x.Element).ToArray();
}
```

Слияние k отсортированных списков, медиана потока (две кучи), планировщик задач — типовые применения.

## Нюансы и подводные камни

- `mid = (lo + hi) / 2` переполняется: `lo + (hi - lo) / 2`.
- Ошибки на границах (`<` vs `<=`, `hi = mid` vs `mid - 1`): выберите инвариант и придерживайтесь.
- `PriorityQueue` в .NET — min-куча: для max используйте отрицательный приоритет или `Comparer`.
- Нет операции «обновить приоритет»: добавляйте повторно и игнорируйте устаревшие.
- Неустойчивая сортировка портит порядок равных элементов.

## Практика

1. Реализуйте бинарный поиск первого/последнего вхождения.
2. Решите: Koko Eating Bananas, Merge K Sorted Lists, Find Median from Data Stream.
3. Сравните `Array.Sort` и `OrderBy` по времени и устойчивости.

## Вопросы с ответами

> [!question]- Какая сортировка в .NET?
> Introsort (quicksort + heapsort + insertion), неустойчивая; `OrderBy` — устойчивая.

> [!question]- Как найти top-k эффективно?
> Куча размера k: O(n log k) вместо полной сортировки O(n log n).

## Связанные темы

- [[N:3ea33104867981f2bab1ca488af03764]]
- [[N:3ea33104867981138adac295272a7a21]]
