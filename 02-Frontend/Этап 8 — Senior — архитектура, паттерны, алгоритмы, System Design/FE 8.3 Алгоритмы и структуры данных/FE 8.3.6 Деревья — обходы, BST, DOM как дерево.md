---
type: topic
domain: frontend
stage: 8
section: "8.3"
order: 6
status: todo
level: senior
notion_id: 3ea3310486798177a027ea99db711b68
tags: [domain/frontend, stage/8, level/senior, topic/algorithms, topic/trees, topic/bst, topic/dom, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Деревья: обходы, BST, DOM как дерево

↑ [[FE 8.3 Алгоритмы и структуры данных|8.3 Алгоритмы и структуры данных]] · ← [[FE 8.3.5 Связные списки|Предыдущая]] · → [[FE 8.3.7 Графы — BFS и DFS|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Деревья — основа DOM, файловых систем, роутинга; нужны обходы и работа с BST.

## Двоичное дерево

```ts
class TreeNode<T> {
  constructor(public val: T, public left: TreeNode<T> | null = null, public right: TreeNode<T> | null = null) {}
}
```

## Обходы

```ts
// DFS: pre-order (корень, левое, правое), in-order (левое, корень, правое), post-order
const inorder = (n: TreeNode<number> | null, out: number[] = []) => {
  if (!n) return out
  inorder(n.left, out); out.push(n.val); inorder(n.right, out)
  return out
}

// DFS итеративно через стек
function preorder(root: TreeNode<number> | null) {
  const out: number[] = [], st = root ? [root] : []
  while (st.length) { const n = st.pop()!; out.push(n.val); if (n.right) st.push(n.right); if (n.left) st.push(n.left) }
  return out
}

// BFS по уровням через очередь
function levels(root: TreeNode<number> | null) {
  const res: number[][] = [], q = root ? [root] : []
  while (q.length) {
    const level: number[] = [], size = q.length
    for (let i = 0; i < size; i++) { const n = q.shift()!; level.push(n.val); n.left && q.push(n.left); n.right && q.push(n.right) }
    res.push(level)
  }
  return res
}

const height = (n: TreeNode<number> | null): number => n ? 1 + Math.max(height(n.left), height(n.right)) : 0
```

## BST (бинарное дерево поиска)

Левые значения < корня < правые. In-order обход даёт отсортированную последовательность. Поиск и вставка O(log n) в сбалансированном, O(n) в вырожденном. Сбалансированные: AVL, красно-чёрные.

```ts
function isBST(n: TreeNode<number> | null, lo = -Infinity, hi = Infinity): boolean {
  if (!n) return true
  if (n.val <= lo || n.val >= hi) return false
  return isBST(n.left, lo, n.val) && isBST(n.right, n.val, hi)
}
```

## DOM как дерево

```ts
// DFS по DOM
function walk(el: Element, fn: (e: Element) => void) { fn(el); for (const c of el.children) walk(c, fn) }

// поиск ближайшего общего предка
const lca = (a: Node, b: Node) => { const p = new Set<Node>(); for (let n: Node | null = a; n; n = n.parentNode) p.add(n); for (let n: Node | null = b; n; n = n.parentNode) if (p.has(n)) return n }
```

Также: `querySelectorAll`, `TreeWalker`, виртуальный DOM (дерево vnode), дерево компонентов, дерево маршрутов.

## Другие деревья

| Структура | Назначение |
|---|---|
| Trie | префиксный поиск, автодополнение |
| Heap | приоритетная очередь |
| Segment tree | запросы на диапазонах |
| B-tree | индексы БД |

## Вопросы с ответами

> [!question]- Какой обход даёт отсортированный результат в BST?
> In-order (левое, корень, правое).

> [!question]- Чем DFS отличается от BFS?
> DFS идёт вглубь (стек или рекурсия), BFS по уровням (очередь). BFS находит кратчайший путь в невзвешенном графе.
