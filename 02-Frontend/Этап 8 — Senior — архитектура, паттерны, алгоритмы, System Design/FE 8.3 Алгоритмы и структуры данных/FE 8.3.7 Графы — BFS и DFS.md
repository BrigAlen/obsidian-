---
type: topic
domain: frontend
stage: 8
section: "8.3"
order: 7
status: todo
level: senior
notion_id: 3ea33104867981dbb894dab32e9a8155
tags: [domain/frontend, stage/8, level/senior, topic/algorithms, topic/graphs, topic/bfs, topic/dfs, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Графы: BFS и DFS

↑ [[FE 8.3 Алгоритмы и структуры данных|8.3 Алгоритмы и структуры данных]] · ← [[FE 8.3.6 Деревья — обходы, BST, DOM как дерево|Предыдущая]] · → [[FE 8.3.8 Рекурсия|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Графы встречаются в зависимостях модулей, маршрутах, задачах на «острова»; знать нужно представление и два обхода.

## Представление

```ts
// список смежности
const graph = new Map<string, string[]>([
  ['A', ['B', 'C']], ['B', ['D']], ['C', ['D']], ['D', []],
])
```

| Представление | Память | Проверка ребра | Обход соседей |
|---|---|---|---|
| Список смежности | O(V + E) | O(deg) | O(deg) |
| Матрица смежности | O(V²) | O(1) | O(V) |

## BFS (в ширину)

```ts
function bfs(g: Map<string, string[]>, start: string) {
  const seen = new Set([start]), q = [start], order: string[] = []
  while (q.length) {
    const v = q.shift()!; order.push(v)
    for (const n of g.get(v) ?? []) if (!seen.has(n)) { seen.add(n); q.push(n) }
  }
  return order
}
```

Кратчайший путь в невзвешенном графе; уровни.

## DFS (в глубину)

```ts
function dfs(g: Map<string, string[]>, v: string, seen = new Set<string>()) {
  seen.add(v)
  for (const n of g.get(v) ?? []) if (!seen.has(n)) dfs(g, n, seen)
  return seen
}
```

Поиск компонент связности, обнаружение циклов, топологическая сортировка.

## Типовые задачи

```ts
// число островов на сетке
function islands(grid: string[][]) {
  let count = 0
  const dfs = (r: number, c: number) => {
    if (r < 0 || c < 0 || r >= grid.length || c >= grid[0].length || grid[r][c] !== '1') return
    grid[r][c] = '0'
    dfs(r + 1, c); dfs(r - 1, c); dfs(r, c + 1); dfs(r, c - 1)
  }
  for (let r = 0; r < grid.length; r++) for (let c = 0; c < grid[0].length; c++) if (grid[r][c] === '1') { count++; dfs(r, c) }
  return count
}
```

- **Топологическая сортировка**: порядок сборки модулей, зависимостей задач (Kahn с входящими степенями);
- **Цикл в направленном графе**: DFS с состояниями white/gray/black;
- **Дейкстра**: кратчайший путь во взвешенном графе с неотрицательными весами (heap), O((V+E) log V);
- **Union-Find**: компоненты связности.

## Во фронтенде

Граф зависимостей бандлера, граф реактивности, маршруты, соцсети, дерево компонентов.

## Вопросы с ответами

> [!question]- Когда BFS, когда DFS?
> BFS — кратчайший путь по числу рёбер, обход по уровням. DFS — обход в глубину, циклы, компоненты, топологическая сортировка, перебор с возвратом.

> [!question]- Как обнаружить циклическую зависимость модулей?
> DFS с отметками состояний (в процессе / завершено); встреча узла «в процессе» означает цикл. Либо топологическая сортировка: если обработаны не все узлы, цикл есть.
