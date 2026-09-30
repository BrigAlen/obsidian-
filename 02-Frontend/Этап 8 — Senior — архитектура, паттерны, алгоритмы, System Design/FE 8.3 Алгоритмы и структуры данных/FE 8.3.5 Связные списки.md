---
type: topic
domain: frontend
stage: 8
section: "8.3"
order: 5
status: todo
level: senior
notion_id: 3ea3310486798148b173e1cc169f8957
tags: [domain/frontend, stage/8, level/senior, topic/algorithms, topic/linked-list, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Связные списки

↑ [[FE 8.3 Алгоритмы и структуры данных|8.3 Алгоритмы и структуры данных]] · ← [[FE 8.3.4 Стек и очередь|Предыдущая]] · → [[FE 8.3.6 Деревья — обходы, BST, DOM как дерево|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Классические задачи: разворот списка, цикл, слияние; проверяют работу с указателями.

## Структура

```ts
class ListNode<T> {
  constructor(public val: T, public next: ListNode<T> | null = null) {}
}
```

| Операция | Массив | Односвязный список |
|---|---|---|
| Доступ по индексу | O(1) | O(n) |
| Вставка/удаление в начале | O(n) | O(1) |
| Вставка после известного узла | O(n) | O(1) |
| Поиск | O(n) | O(n) |

Двусвязный список хранит ссылку `prev`: удаление узла O(1) при известном узле (LRU-кэш).

## Типовые задачи

```ts
// разворот
function reverse<T>(head: ListNode<T> | null) {
  let prev: ListNode<T> | null = null
  while (head) { const next = head.next; head.next = prev; prev = head; head = next }
  return prev
}

// цикл (Floyd: медленный и быстрый указатели)
function hasCycle<T>(head: ListNode<T> | null) {
  let slow = head, fast = head
  while (fast?.next) { slow = slow!.next; fast = fast.next.next; if (slow === fast) return true }
  return false
}

// середина списка
function middle<T>(head: ListNode<T> | null) {
  let s = head, f = head
  while (f?.next) { s = s!.next; f = f.next.next }
  return s
}

// слияние двух отсортированных
function merge(a: ListNode<number> | null, b: ListNode<number> | null) {
  const dummy = new ListNode(0); let t = dummy
  while (a && b) { if (a.val <= b.val) { t.next = a; a = a.next } else { t.next = b; b = b.next }; t = t.next }
  t.next = a ?? b
  return dummy.next
}
```

Приём **dummy-узла** упрощает крайние случаи (пустой список, удаление головы).

## LRU-кэш

`Map` + порядок вставки в JS:

```ts
class LRU<K, V> {
  #m = new Map<K, V>()
  constructor(private cap: number) {}
  get(k: K) { if (!this.#m.has(k)) return; const v = this.#m.get(k)!; this.#m.delete(k); this.#m.set(k, v); return v }
  set(k: K, v: V) {
    this.#m.delete(k); this.#m.set(k, v)
    if (this.#m.size > this.cap) this.#m.delete(this.#m.keys().next().value!)
  }
}
```

Классическая реализация — хэш-таблица + двусвязный список: O(1) для `get` и `set`.

## Вопросы с ответами

> [!question]- Как определить цикл в списке?
> Алгоритм Флойда: медленный указатель по одному шагу, быстрый по два. Если встретятся, цикл есть. O(n) времени, O(1) памяти.

> [!question]- Когда список лучше массива?
> Частые вставки и удаления в середине или начале при известном узле. На практике массивы быстрее из-за локальности кэша.
