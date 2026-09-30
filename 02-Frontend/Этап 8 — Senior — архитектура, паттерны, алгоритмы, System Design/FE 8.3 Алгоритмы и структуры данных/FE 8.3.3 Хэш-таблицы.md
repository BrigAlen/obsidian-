---
type: topic
domain: frontend
stage: 8
section: "8.3"
order: 3
status: todo
level: senior
notion_id: 3ea331048679813f8173db48be1d07d2
tags: [domain/frontend, stage/8, level/senior, topic/algorithms, topic/hash-table, topic/map, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Хэш-таблицы

↑ [[FE 8.3 Алгоритмы и структуры данных|8.3 Алгоритмы и структуры данных]] · ← [[FE 8.3.2 Массивы и строки — два указателя, скользящее окно|Предыдущая]] · → [[FE 8.3.4 Стек и очередь|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Хэш-таблица — главный инструмент оптимизации O(n²) до O(n).

## Принцип

Ключ превращается хэш-функцией в индекс «корзины». Операции вставки, поиска и удаления — O(1) в среднем.

## Коллизии

- **цепочки** (chaining): в корзине список;
- **открытая адресация**: ищем следующую свободную ячейку;
- при росте коэффициента заполнения — **rehash** (увеличение таблицы).

## В JS

```ts
const m = new Map<string, number>()
m.set('a', 1); m.get('a'); m.has('a'); m.delete('a'); m.size

const s = new Set<number>([1, 2, 2, 3])   // уникальные значения

// Map лучше объекта для произвольных ключей: любой тип ключа, порядок вставки, size, нет прототипных ключей
const o = Object.create(null) as Record<string, number>
```

`WeakMap` и `WeakSet` — ключи-объекты без удержания в памяти (кэши, приватные данные).

## Типовые задачи

```ts
// Two Sum: индексы двух чисел с суммой target, O(n)
function twoSum(a: number[], target: number) {
  const idx = new Map<number, number>()
  for (let i = 0; i < a.length; i++) {
    const j = idx.get(target - a[i])
    if (j !== undefined) return [j, i]
    idx.set(a[i], i)
  }
}

// частоты символов и анаграммы
const freq = (s: string) => { const m = new Map<string, number>(); for (const c of s) m.set(c, (m.get(c) ?? 0) + 1); return m }

// группировка анаграмм
const groups = new Map<string, string[]>()
for (const w of words) {
  const k = [...w].sort().join('')
  groups.set(k, [...(groups.get(k) ?? []), w])
}
```

Паттерны: подсчёт, дедупликация, «уже видели», поиск пары, кэш результатов, индексация по ключу.

## Нюансы

- порядок итерации в объекте: сначала целочисленные ключи по возрастанию, потом строки в порядке вставки; в `Map` — порядок вставки;
- ключи-объекты в `Map` сравниваются по ссылке;
- `NaN` в `Set` и `Map` считается равным самому себе.

## Вопросы с ответами

> [!question]- Почему доступ по ключу в хэш-таблице O(1)?
> Хэш определяет корзину напрямую, без перебора. В среднем в корзине немного элементов, но при плохой хэш-функции возможна деградация до O(n).

> [!question]- Чем Map лучше обычного объекта?
> Ключи любых типов, сохранение порядка, `size`, нет конфликтов с прототипом, лучше для частых добавлений и удалений.
