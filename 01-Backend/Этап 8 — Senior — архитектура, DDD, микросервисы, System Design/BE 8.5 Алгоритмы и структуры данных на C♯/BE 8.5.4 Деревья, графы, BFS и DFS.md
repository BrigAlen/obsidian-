---
type: topic
domain: backend
stage: 8
section: "8.5"
order: 4
status: todo
level: senior
notion_id: 3ea33104867981f2bab1ca488af03764
tags: [domain/backend, stage/8, level/senior, topic/algorithms, topic/trees, topic/graphs, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# Деревья, графы, BFS и DFS

↑ [[BE 8.5 Алгоритмы и структуры данных на C♯|8.5 Алгоритмы и структуры данных на C♯]] · ← [[BE 8.5.3 Хэширование — Dictionary и HashSet в задачах|Предыдущая]] · → [[BE 8.5.5 Сортировка, бинарный поиск, PriorityQueue|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> Обходы деревьев и графов — стандартный блок алгоритмических задач.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Дерево**: связный граф без циклов; бинарное дерево — не более двух потомков; BST — левое < корень < правое.

```csharp
public class Node { public int Val; public Node? Left, Right; }

// DFS рекурсивно: глубина
static int Depth(Node? n) => n is null ? 0 : 1 + Math.Max(Depth(n.Left), Depth(n.Right));

// Обходы: pre-order (корень, лево, право), in-order (для BST — по возрастанию), post-order
static void InOrder(Node? n, List<int> res) { if (n is null) return; InOrder(n.Left, res); res.Add(n.Val); InOrder(n.Right, res); }

// BFS по уровням (очередь)
static IList<IList<int>> Levels(Node? root)
{
    var res = new List<IList<int>>(); if (root is null) return res;
    var q = new Queue<Node>(); q.Enqueue(root);
    while (q.Count > 0)
    {
        var level = new List<int>();
        for (int i = q.Count; i > 0; i--) { var n = q.Dequeue(); level.Add(n.Val); if (n.Left != null) q.Enqueue(n.Left); if (n.Right != null) q.Enqueue(n.Right); }
        res.Add(level);
    }
    return res;
}
```

**Граф**: вершины и рёбра; представление — список смежности `Dictionary<int, List<int>>` (разреженный) или матрица (плотный).

```csharp
// BFS: кратчайший путь по числу рёбер в невзвешенном графе
static int ShortestPath(Dictionary<int, List<int>> g, int s, int t)
{
    var dist = new Dictionary<int, int> { [s] = 0 };
    var q = new Queue<int>(); q.Enqueue(s);
    while (q.Count > 0)
    {
        var u = q.Dequeue(); if (u == t) return dist[u];
        foreach (var v in g.GetValueOrDefault(u) ?? [])
            if (dist.TryAdd(v, dist[u] + 1)) q.Enqueue(v);
    }
    return -1;
}

// DFS итеративно (стек), счёт компонент связности; для островов в сетке — заливка
```

| Алгоритм | Применение | Сложность |
|---|---|---|
| BFS | кратчайший путь (невзвешенный), уровни | O(V+E) |
| DFS | компоненты, циклы, топологическая сортировка, backtracking | O(V+E) |
| Dijkstra | кратчайший путь с неотрицательными весами (`PriorityQueue`) | O((V+E) log V) |
| Union-Find | связность, компоненты | почти O(1) на операцию |
| Топологическая сортировка | зависимости (граф без циклов) | O(V+E) |

## Нюансы и подводные камни

- Рекурсия DFS на глубоком графе даёт `StackOverflow`: используйте итеративный вариант.
- Помечайте посещённые вершины при постановке в очередь, а не при извлечении.
- Циклы в графе: без `visited` бесконечный обход.
- BST вырождается в список при отсортированной вставке (нужна балансировка).

## Практика

1. Решите: Max Depth, Level Order, Number of Islands, Course Schedule (топосорт).
2. Реализуйте Dijkstra на `PriorityQueue`.
3. Проверьте, является ли дерево корректным BST.

## Вопросы с ответами

> [!question]- BFS или DFS?
> BFS — кратчайший путь по числу рёбер и обход по уровням; DFS — глубина, компоненты, циклы, перебор с возвратом.

> [!question]- Как найти цикл в ориентированном графе?
> DFS с тремя состояниями вершины (не посещена/в стеке/завершена).

## Связанные темы

- [[N:3ea33104867981c79650f64aae90de85]]
- [[N:3ea3310486798163bed2e35a8324595b]]
