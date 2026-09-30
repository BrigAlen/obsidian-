---
type: topic
domain: frontend
stage: 8
section: "8.3"
order: 11
status: todo
level: senior
notion_id: 3ea3310486798146a788c8ea6e4400f3
tags: [domain/frontend, stage/8, level/senior, topic/algorithms, topic/leetcode, topic/interview, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Типовые задачи LeetCode для фронтенда

↑ [[FE 8.3 Алгоритмы и структуры данных|8.3 Алгоритмы и структуры данных]] · ← [[FE 8.3.10 Динамическое программирование и мемоизация|Предыдущая]] · → [[FE 8.3.12 Шпаргалка по алгоритмам перед собесом|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Во фронтенд-интервью чаще встречаются практичные задачи: утилиты JS, работа с DOM, массивы и строки, а не сложные графы.

## Утилиты на JS

```ts
// debounce и throttle
const debounce = <A extends unknown[]>(fn: (...a: A) => void, ms: number) => {
  let t: ReturnType<typeof setTimeout>
  return (...a: A) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms) }
}
const throttle = <A extends unknown[]>(fn: (...a: A) => void, ms: number) => {
  let last = 0
  return (...a: A) => { const now = Date.now(); if (now - last >= ms) { last = now; fn(...a) } }
}

// Promise.all своими руками
const promiseAll = <T>(ps: Promise<T>[]) => new Promise<T[]>((res, rej) => {
  const out: T[] = []; let done = 0
  if (!ps.length) return res(out)
  ps.forEach((p, i) => Promise.resolve(p).then(v => { out[i] = v; if (++done === ps.length) res(out) }, rej))
})

// EventEmitter
class Emitter {
  #h = new Map<string, Set<Function>>()
  on(e: string, f: Function) { (this.#h.get(e) ?? this.#h.set(e, new Set()).get(e)!).add(f); return () => this.off(e, f) }
  off(e: string, f: Function) { this.#h.get(e)?.delete(f) }
  emit(e: string, ...a: unknown[]) { this.#h.get(e)?.forEach(f => f(...a)) }
}

// каррирование, deepEqual, flatten, groupBy, pick/omit, chunk, uniq
const chunk = <T>(a: T[], n: number) => Array.from({ length: Math.ceil(a.length / n) }, (_, i) => a.slice(i * n, i * n + n))
```

## Классика

| Задача | Приём |
|---|---|
| Two Sum | хэш-таблица |
| Valid Parentheses | стек |
| Merge Intervals | сортировка, слияние |
| Reverse Linked List | указатели |
| Longest Substring Without Repeating | скользящее окно |
| Group Anagrams | ключ из отсортированной строки |
| Binary Search | границы |
| Number of Islands | DFS/BFS |
| Climbing Stairs, Coin Change | ДП |
| LRU Cache | Map или список + хэш |
| Top K Frequent | частоты + heap/сортировка |
| Flatten Nested Array | рекурсия/стек |
| Deep Clone / Deep Equal | рекурсия, циклы, типы |

## DOM-задачи

- обход дерева и поиск элемента по условию, `getElementsByClassName` вручную;
- делегирование событий;
- ленивая подгрузка через `IntersectionObserver`;
- реализация `bind`, `call`, `apply`, `new`, `instanceof`;
- виртуальный список, дерево-компонент, автокомплит, star rating.

## Как решать на собесе

1. Уточнить условия, размеры, крайние случаи.
2. Озвучить наивное решение и его сложность.
3. Предложить оптимизацию и обосновать.
4. Написать код, называя переменные осмысленно.
5. Проверить на примерах и граничных случаях.
6. Назвать время и память.

## Вопросы с ответами

> [!question]- Чем debounce отличается от throttle?
> Debounce выполняет функцию после паузы в вызовах, throttle — не чаще одного раза за интервал.

> [!question]- Как решить Top K Frequent?
> Подсчитать частоты в Map, затем взять K самых частых: сортировка O(n log n), heap O(n log k) или bucket sort O(n).
