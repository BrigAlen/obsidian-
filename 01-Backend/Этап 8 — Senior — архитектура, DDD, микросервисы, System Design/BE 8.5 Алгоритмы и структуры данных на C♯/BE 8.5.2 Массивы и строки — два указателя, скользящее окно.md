---
type: topic
domain: backend
stage: 8
section: "8.5"
order: 2
status: todo
level: senior
notion_id: 3ea331048679819daa86c3ba7f89d3c4
tags: [domain/backend, stage/8, level/senior, topic/algorithms, topic/arrays, topic/two-pointers, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# Массивы и строки: два указателя, скользящее окно

↑ [[BE 8.5 Алгоритмы и структуры данных на C♯|8.5 Алгоритмы и структуры данных на C♯]] · ← [[BE 8.5.1 Big O и коллекции .NET|Предыдущая]] · → [[BE 8.5.3 Хэширование — Dictionary и HashSet в задачах|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Самые частые задачи live coding: массивы и строки решаются двумя указателями и окном.

## Объяснение

**Два указателя** — два индекса, двигающихся по массиву, чтобы заменить вложенные циклы O(n²) на O(n).

```csharp
// Два числа с суммой target в отсортированном массиве
static (int, int)? TwoSum(int[] a, int target)
{
    int l = 0, r = a.Length - 1;
    while (l < r)
    {
        var s = a[l] + a[r];
        if (s == target) return (l, r);
        if (s < target) l++; else r--;
    }
    return null;
}

// Разворот и проверка палиндрома
static bool IsPalindrome(string s)
{
    int l = 0, r = s.Length - 1;
    while (l < r)
    {
        while (l < r && !char.IsLetterOrDigit(s[l])) l++;
        while (l < r && !char.IsLetterOrDigit(s[r])) r--;
        if (char.ToLower(s[l++]) != char.ToLower(s[r--])) return false;
    }
    return true;
}
```

**Скользящее окно** — подмассив/подстрока с двумя границами, которые сдвигаются вперёд.

```csharp
// Самая длинная подстрока без повторяющихся символов — O(n)
static int LongestUnique(string s)
{
    var last = new Dictionary<char, int>();
    int best = 0, left = 0;
    for (int right = 0; right < s.Length; right++)
    {
        if (last.TryGetValue(s[right], out var idx) && idx >= left) left = idx + 1;
        last[s[right]] = right;
        best = Math.Max(best, right - left + 1);
    }
    return best;
}

// Максимальная сумма подмассива длины k
static int MaxSum(int[] a, int k)
{
    int sum = a.Take(k).Sum(), best = sum;
    for (int i = k; i < a.Length; i++) { sum += a[i] - a[i - k]; best = Math.Max(best, sum); }
    return best;
}
```

Другие приёмы: префиксные суммы (`prefix[i]` — сумма первых i элементов, диапазон за O(1)), быстрый и медленный указатели (цикл в списке), сортировка + указатели (3Sum), разворот на месте.

## Нюансы и подводные камни

- Границы: пустой массив, один элемент, повторы.
- Переполнение `int` при суммах: используйте `long`.
- Строки в C# неизменяемы: конкатенация в цикле O(n²), используйте `StringBuilder`/`Span`.
- Различие Unicode и `char` (суррогатные пары).

## Практика

1. Решите: 3Sum, Container With Most Water, Minimum Window Substring.
2. Реализуйте префиксные суммы для запросов суммы на диапазоне.
3. Найдите цикл в связном списке двумя указателями.

## Вопросы с ответами

> [!question]- Когда применять два указателя?
> Когда структура отсортирована или можно двигать границы монотонно, чтобы исключить вложенный перебор.

> [!question]- Чем скользящее окно отличается от двух указателей?
> Окно двигает обе границы в одном направлении и поддерживает инвариант состояния внутри окна.

## Связанные темы

- [[N:3ea3310486798147b462ffb4f50ae8e3]]
- [[N:3ea33104867981c79650f64aae90de85]]
