---
type: topic
domain: frontend
stage: 8
section: "8.3"
order: 9
status: todo
level: senior
notion_id: 3ea33104867981cfb5d5d78feca9a354
tags: [domain/frontend, stage/8, level/senior, topic/algorithms, topic/sorting, topic/binary-search, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Сортировки и бинарный поиск

↑ [[FE 8.3 Алгоритмы и структуры данных|8.3 Алгоритмы и структуры данных]] · ← [[FE 8.3.8 Рекурсия|Предыдущая]] · → [[FE 8.3.10 Динамическое программирование и мемоизация|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Ожидают знание базовых сортировок и особенностей `Array.prototype.sort`, а бинарный поиск — универсальный приём.

## Сортировки

| Алгоритм | Среднее | Худшее | Память | Устойчив |
|---|---|---|---|---|
| Bubble / Insertion / Selection | O(n²) | O(n²) | O(1) | bubble, insertion — да |
| Merge sort | O(n log n) | O(n log n) | O(n) | да |
| Quick sort | O(n log n) | O(n²) | O(log n) | нет |
| Heap sort | O(n log n) | O(n log n) | O(1) | нет |
| Counting / Radix | O(n + k) | O(n + k) | O(k) | да |

```ts
function mergeSort(a: number[]): number[] {
  if (a.length < 2) return a
  const m = a.length >> 1, l = mergeSort(a.slice(0, m)), r = mergeSort(a.slice(m))
  const out: number[] = []; let i = 0, j = 0
  while (i < l.length && j < r.length) out.push(l[i] <= r[j] ? l[i++] : r[j++])
  return out.concat(l.slice(i), r.slice(j))
}

function quickSort(a: number[]): number[] {
  if (a.length < 2) return a
  const p = a[a.length >> 1]
  return [...quickSort(a.filter(x => x < p)), ...a.filter(x => x === p), ...quickSort(a.filter(x => x > p))]
}
```

## Array.prototype.sort

- по умолчанию сравнивает **как строки**: `[10, 9, 1].sort()` → `[1, 10, 9]`;
- нужен компаратор: `arr.sort((a, b) => a - b)`;
- сортирует **на месте**; `toSorted()` возвращает копию;
- с ES2019 стабильна (равные элементы сохраняют порядок); V8 использует TimSort;
- сортировка строк с локалью: `a.localeCompare(b, 'ru')`.

## Бинарный поиск

Массив отсортирован; на каждом шаге отбрасываем половину. O(log n).

```ts
function binarySearch(a: number[], x: number): number {
  let lo = 0, hi = a.length - 1
  while (lo <= hi) {
    const mid = lo + ((hi - lo) >> 1)
    if (a[mid] === x) return mid
    a[mid] < x ? (lo = mid + 1) : (hi = mid - 1)
  }
  return -1
}

// левая граница: первый индекс, где a[i] >= x
function lowerBound(a: number[], x: number) {
  let lo = 0, hi = a.length
  while (lo < hi) { const m = (lo + hi) >> 1; a[m] < x ? (lo = m + 1) : (hi = m) }
  return lo
}
```

Бинарный поиск **по ответу**: минимальная скорость, при которой выполнимо условие (монотонная функция).

## Вопросы с ответами

> [!question]- Почему [10, 9, 1].sort() даёт [1, 10, 9]?
> Без компаратора элементы приводятся к строкам и сравниваются лексикографически. Нужен `(a, b) => a - b`.

> [!question]- Что такое устойчивая сортировка и зачем она?
> Равные элементы сохраняют исходный порядок. Важно при многоуровневой сортировке (сначала по одному полю, потом по другому).
