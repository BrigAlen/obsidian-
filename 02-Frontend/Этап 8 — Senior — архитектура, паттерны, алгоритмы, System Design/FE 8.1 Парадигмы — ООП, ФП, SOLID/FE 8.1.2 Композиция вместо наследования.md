---
type: topic
domain: frontend
stage: 8
section: "8.1"
order: 2
status: todo
level: senior
notion_id: 3ea3310486798134a70fe6c06572b135
tags: [domain/frontend, stage/8, level/senior, topic/composition, topic/design, topic/vue, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Композиция вместо наследования

↑ [[FE 8.1 Парадигмы — ООП, ФП, SOLID|8.1 Парадигмы: ООП, ФП, SOLID]] · ← [[FE 8.1.1 ООП — инкапсуляция, наследование, полиморфизм, абстракция|Предыдущая]] · → [[FE 8.1.3 SOLID подробно с примерами|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Ключевой принцип проектирования: спрашивают, чем композиция лучше и как это выглядит во Vue.

## Проблема наследования

- жёсткая связь подкласса с реализацией родителя;
- комбинаторный взрыв классов (`AdminUserWithAudit`, `GuestUserWithCache`);
- нельзя унаследовать сразу от нескольких;
- изменения в базовом классе ломают всех потомков.

## Композиция

Собираем поведение из небольших независимых частей.

```ts
// вместо class ExportableSortableTable extends Table
const useSort = <T>(items: Ref<T[]>) => { /* ... */ }
const useExport = <T>(items: Ref<T[]>) => { /* ... */ }
const usePaging = <T>(items: Ref<T[]>) => { /* ... */ }

function useTable<T>(source: Ref<T[]>) {
  const sorted = useSort(source)
  const paged = usePaging(sorted.items)
  const exporter = useExport(paged.pageItems)
  return { ...sorted, ...paged, ...exporter }
}
```

## Композиция во Vue

| Механизм | Что композирует |
|---|---|
| **Composables** | логика с состоянием |
| **Slots** | разметка |
| **Props / events** | контракт компонента |
| **provide / inject** | зависимости через дерево |
| **Директивы, plugins** | сквозное поведение |

Замена mixins: они давали конфликты имён и неявные источники данных, composables явные.

## Когда наследование оправдано

Устойчивая иерархия «является» (is-a) с общими инвариантами, а не переиспользование кода. Ещё вариант — базовые классы фреймворка (например `HTMLElement` для Web Components).

## Практика

- используйте небольшие интерфейсы и функции;
- зависимость через параметр, а не через наследование;
- decorator, strategy, adapter — паттерны композиции.

## Вопросы с ответами

> [!question]- Почему «композиция вместо наследования»?
> Слабее связность, проще тестировать, можно комбинировать поведения, нет хрупкого базового класса.

> [!question]- Чем composable лучше mixin?
> Явные входы и выходы, нет конфликтов имён, понятный источник каждого значения, типизация.
