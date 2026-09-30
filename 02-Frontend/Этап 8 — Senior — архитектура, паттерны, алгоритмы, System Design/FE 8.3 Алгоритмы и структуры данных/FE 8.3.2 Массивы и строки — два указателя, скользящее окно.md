---
type: topic
domain: frontend
stage: 8
section: "8.3"
order: 2
status: todo
level: senior
notion_id: 3ea33104867981c9bd75f33273cc8cd1
tags: [domain/frontend, stage/8, level/senior, topic/algorithms, topic/arrays, topic/two-pointers, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# Массивы и строки: два указателя, скользящее окно

↑ [[FE 8.3 Алгоритмы и структуры данных|8.3 Алгоритмы и структуры данных]] · ← [[FE 8.3.1 Сложность алгоритмов — Big O|Предыдущая]] · → [[FE 8.3.3 Хэш-таблицы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Самый частый тип задач на собеседовании; знание двух приёмов закрывает большую часть.

## Два указателя

Два индекса движутся по массиву навстречу друг другу или в одном направлении. Сложность O(n), память O(1).

```ts
// проверка палиндрома
function isPalindrome(s: string): boolean {
  let l = 0, r = s.length - 1
  while (l < r) {
    if (s[l] !== s[r]) return false
    l++; r--
  }
  return true
}

// два числа с суммой target в отсортированном массиве
function twoSum(a: number[], target: number): [number, number] | null {
  let l = 0, r = a.length - 1
  while (l < r) {
    const s = a[l] + a[r]
    if (s === target) return [l, r]
    s < target ? l++ : r--
  }
  return null
}

// удаление дубликатов на месте (быстрый и медленный указатель)
function dedupe(a: number[]): number {
  let w = 0
  for (let i = 0; i < a.length; i++) if (i === 0 || a[i] !== a[i - 1]) a[w++] = a[i]
  return w
}
```

## Скользящее окно

Подмассив/подстрока непрерывной длины: окно расширяем правым концом и сужаем левым.

```ts
// максимальная сумма подмассива длины k
function maxSum(a: number[], k: number): number {
  let sum = a.slice(0, k).reduce((x, y) => x + y, 0), best = sum
  for (let i = k; i < a.length; i++) { sum += a[i] - a[i - k]; best = Math.max(best, sum) }
  return best
}

// самая длинная подстрока без повторов
function longestUnique(s: string): number {
  const seen = new Map<string, number>()
  let l = 0, best = 0
  for (let r = 0; r < s.length; r++) {
    if (seen.has(s[r]) && seen.get(s[r])! >= l) l = seen.get(s[r])! + 1
    seen.set(s[r], r)
    best = Math.max(best, r - l + 1)
  }
  return best
}
```

## Когда что применять

| Признак | Приём |
|---|---|
| Отсортированный массив, пары, палиндром | два указателя |
| «Непрерывный подмассив/подстрока» и условие | скользящее окно |
| Подсчёт, поиск дубликатов | хэш-таблица |
| Диапазонные суммы | префиксные суммы |

## Префиксные суммы

```ts
const pref = [0]; for (const x of a) pref.push(pref.at(-1)! + x)
const rangeSum = (l: number, r: number) => pref[r + 1] - pref[l]   // O(1) запрос
```

## Вопросы с ответами

> [!question]- Как найти самую длинную подстроку без повторяющихся символов?
> Скользящее окно с `Map` последних позиций символов: правый указатель идёт вперёд, левый прыгает за последнее повторение. O(n).

> [!question]- Чем два указателя лучше вложенных циклов?
> Каждый указатель проходит массив один раз, поэтому O(n) вместо O(n²).
