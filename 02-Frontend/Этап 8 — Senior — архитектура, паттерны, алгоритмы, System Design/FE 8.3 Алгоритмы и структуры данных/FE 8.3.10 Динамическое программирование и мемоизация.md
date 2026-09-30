---
type: topic
domain: frontend
stage: 8
section: "8.3"
order: 10
status: todo
level: senior
notion_id: 3ea33104867981e98cdbc2dfac529ee1
tags: [domain/frontend, stage/8, level/senior, topic/algorithms, topic/dp, topic/memoization, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Динамическое программирование и мемоизация

↑ [[FE 8.3 Алгоритмы и структуры данных|8.3 Алгоритмы и структуры данных]] · ← [[FE 8.3.9 Сортировки и бинарный поиск|Предыдущая]] · → [[FE 8.3.11 Типовые задачи LeetCode для фронтенда|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> ДП — «сложная» тема; достаточно уметь распознавать перекрывающиеся подзадачи и записывать переход.

## Признаки

- **оптимальная подструктура**: решение строится из решений подзадач;
- **перекрывающиеся подзадачи**: одни и те же вычисления повторяются;
- вопросы «сколько способов», «минимальное/максимальное», «можно ли».

## Два подхода

**Top-down (мемоизация)**: рекурсия + кэш.

```ts
const fib = (() => {
  const memo = new Map<number, number>()
  const f = (n: number): number => n < 2 ? n : memo.get(n) ?? (memo.set(n, f(n - 1) + f(n - 2)), memo.get(n)!)
  return f
})()
```

**Bottom-up (табуляция)**: заполняем таблицу от малых задач.

```ts
function fibIter(n: number) {
  let a = 0, b = 1
  for (let i = 0; i < n; i++) [a, b] = [b, a + b]
  return a
}
```

## Схема решения

1. Определить состояние `dp[i]` (что означает).
2. Записать переход (рекуррентное соотношение).
3. Задать базовые значения.
4. Порядок вычисления и ответ.
5. Оптимизировать память (часто только предыдущая строка).

## Классические задачи

```ts
// ступеньки: способы подняться на n ступеней шагами 1 или 2
function climb(n: number) { let a = 1, b = 1; for (let i = 2; i <= n; i++) [a, b] = [b, a + b]; return b }

// размен монет: минимум монет
function coinChange(coins: number[], amount: number) {
  const dp = new Array(amount + 1).fill(Infinity); dp[0] = 0
  for (let s = 1; s <= amount; s++) for (const c of coins) if (c <= s) dp[s] = Math.min(dp[s], dp[s - c] + 1)
  return dp[amount] === Infinity ? -1 : dp[amount]
}

// наибольшая общая подпоследовательность
function lcs(a: string, b: string) {
  const dp = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0))
  for (let i = 1; i <= a.length; i++) for (let j = 1; j <= b.length; j++)
    dp[i][j] = a[i - 1] === b[j - 1] ? dp[i - 1][j - 1] + 1 : Math.max(dp[i - 1][j], dp[i][j - 1])
  return dp[a.length][b.length]
}
```

Другие: рюкзак, максимальная сумма подмассива (Кадане), расстояние Левенштейна, longest increasing subsequence, поиск подстроки.

## Мемоизация во фронтенде

```ts
function memoize<A extends unknown[], R>(fn: (...a: A) => R) {
  const cache = new Map<string, R>()
  return (...args: A) => {
    const k = JSON.stringify(args)
    if (!cache.has(k)) cache.set(k, fn(...args))
    return cache.get(k)!
  }
}
```

`computed` во Vue, селекторы, `React.useMemo` — тот же принцип; ограничение кэша (LRU), чистота функции.

## Вопросы с ответами

> [!question]- Чем ДП отличается от жадного алгоритма?
> ДП перебирает подзадачи и выбирает лучшее из них, жадный берёт локально лучший шаг без пересмотра. Жадный быстрее, но верен не всегда.

> [!question]- Как перейти от рекурсии к ДП?
> Найти повторяющиеся подзадачи, добавить мемоизацию, затем при необходимости перевести в таблицу и сократить память.
