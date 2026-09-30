---
type: topic
domain: frontend
stage: 8
section: "8.3"
order: 8
status: todo
level: senior
notion_id: 3ea33104867981899f84ee36308890a8
tags: [domain/frontend, stage/8, level/senior, topic/algorithms, topic/recursion, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Рекурсия

↑ [[FE 8.3 Алгоритмы и структуры данных|8.3 Алгоритмы и структуры данных]] · ← [[FE 8.3.7 Графы — BFS и DFS|Предыдущая]] · → [[FE 8.3.9 Сортировки и бинарный поиск|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Рекурсия лежит в основе деревьев, перебора и ДП; спрашивают базовый случай, стек и оптимизации.

## Структура

1. **Базовый случай** — условие остановки.
2. **Шаг рекурсии** — вызов на меньшей задаче.
3. **Сходимость** — каждый вызов приближается к базе.

```ts
const factorial = (n: number): number => n <= 1 ? 1 : n * factorial(n - 1)

const flatten = (arr: unknown[]): unknown[] =>
  arr.reduce<unknown[]>((acc, x) => acc.concat(Array.isArray(x) ? flatten(x) : x), [])

function deepClone<T>(v: T): T {
  if (v === null || typeof v !== 'object') return v
  if (Array.isArray(v)) return v.map(deepClone) as T
  return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, deepClone(x)])) as T
}
```

## Стек вызовов

Каждый вызов занимает кадр стека. Глубина в JS ограничена (порядка 10 000 кадров): `RangeError: Maximum call stack size exceeded`. JS не гарантирует **оптимизацию хвостовой рекурсии** (TCO).

## Ограничения и обход

- переписать в цикл с явным стеком;
- **мемоизация** для повторяющихся подзадач;
- батчирование через `setTimeout` (trampolining);
- ограничить глубину.

```ts
// trampoline
const trampoline = (f: Function) => (...a: any[]) => { let r = f(...a); while (typeof r === 'function') r = r(); return r }
```

## Перебор с возвратом (backtracking)

```ts
function permutations(a: number[]): number[][] {
  const res: number[][] = []
  const used = new Array(a.length).fill(false)
  const cur: number[] = []
  const go = () => {
    if (cur.length === a.length) return void res.push([...cur])
    for (let i = 0; i < a.length; i++) {
      if (used[i]) continue
      used[i] = true; cur.push(a[i]); go(); cur.pop(); used[i] = false
    }
  }
  go()
  return res
}
```

Подсказка: «все комбинации», «подмножества», «расстановки» → backtracking.

## Сложность

Наивный Фибоначчи O(2ⁿ), с мемоизацией O(n). Считайте число вызовов.

## Вопросы с ответами

> [!question]- Почему возникает переполнение стека?
> Слишком глубокая рекурсия или отсутствие базового случая. Решения: цикл с явным стеком, уменьшение глубины, мемоизация.

> [!question]- Что такое хвостовая рекурсия?
> Рекурсивный вызов — последнее действие функции; в языках с TCO стек не растёт. В JS (кроме Safari) оптимизации нет.
