---
type: topic
domain: frontend
stage: 8
section: "8.3"
order: 4
status: todo
level: senior
notion_id: 3ea33104867981698b9dcf67de00e30c
tags: [domain/frontend, stage/8, level/senior, topic/algorithms, topic/stack, topic/queue, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Стек и очередь

↑ [[FE 8.3 Алгоритмы и структуры данных|8.3 Алгоритмы и структуры данных]] · ← [[FE 8.3.3 Хэш-таблицы|Предыдущая]] · → [[FE 8.3.5 Связные списки|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Стек лежит в основе call stack, undo, парсинга; очередь — в event loop и обходе в ширину.

## Стек (LIFO)

Последним пришёл — первым вышел. Операции push, pop, peek — O(1).

```ts
const stack: number[] = []
stack.push(1); stack.push(2); stack.pop()   // 2
```

Применение: история (undo), call stack, обход в глубину без рекурсии, разбор выражений, проверка скобок, «Next Greater Element» (монотонный стек).

```ts
function validBrackets(s: string): boolean {
  const pairs: Record<string, string> = { ')': '(', ']': '[', '}': '{' }
  const st: string[] = []
  for (const c of s) {
    if ('([{'.includes(c)) st.push(c)
    else if (st.pop() !== pairs[c]) return false
  }
  return st.length === 0
}
```

## Очередь (FIFO)

Первым пришёл — первым вышел.

```ts
// массив: shift() O(n) на больших данных, лучше реализация на связном списке или двух индексах
class Queue<T> {
  #items = new Map<number, T>(); #head = 0; #tail = 0
  enqueue(x: T) { this.#items.set(this.#tail++, x) }
  dequeue(): T | undefined { const v = this.#items.get(this.#head); this.#items.delete(this.#head++); return v }
  get size() { return this.#tail - this.#head }
}
```

Применение: BFS, очередь задач, буфер событий, event loop (macro/microtask queues), rate limiting.

## Варианты

- **Deque**: вставка и удаление с обоих концов;
- **Приоритетная очередь** (heap): извлечение минимума за O(log n), планировщики, Top-K;
- **Кольцевой буфер**: фиксированный размер, логи.

## Задача: очередь на двух стеках

Добавляем в `in`, при `dequeue` переливаем в `out`, если пуст. Амортизированно O(1).

## Вопросы с ответами

> [!question]- Как реализовать undo/redo?
> Два стека: `undo` и `redo`. При действии кладём в `undo` и очищаем `redo`; при отмене переносим между стеками.

> [!question]- Почему shift() на большом массиве медленный?
> Смещает все элементы на одну позицию, O(n). Для очереди лучше связный список или индексы.
