---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981d98f3ff4b0b75829f7
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/reactivity, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Реактивность: ref, reactive, shallowRef, toRef, toRefs

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.4 script setup и макросы компилятора|Предыдущая]] · → [[FE 4.1.6 computed|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















> [!info] Зачем это на собесе
> Ядро Vue: как работает реактивность, когда `ref`, когда `reactive`, что такое `.value`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Реактивность Vue 3 основана на `Proxy`: чтение внутри эффекта регистрирует зависимость (**track**), запись уведомляет подписчиков (**trigger**).

```ts
import { ref, reactive, toRef, toRefs, shallowRef, shallowReactive, readonly, isRef, unref, toRaw, triggerRef } from "vue";

const count = ref(0);                    // count.value
count.value++;
const user = reactive({ name: "A", address: { city: "M" } });   // прокси объекта, без .value
user.address.city = "SPb";                                        // глубокая реактивность

const state = reactive({ a: 1, b: 2 });
const a = toRef(state, "a");              // ref, связанный с полем (реактивность сохраняется)
const { a: a2, b } = toRefs(state);       // все поля как refs — безопасная деструктуризация

const big = shallowRef(hugeObject);       // реактивно только .value = ...; внутренности не отслеживаются
big.value = { ...big.value };             // замена триггерит; мутация — нет (triggerRef(big))
const ro = readonly(state);
```

| API | Назначение |
|---|---|
| `ref(x)` | контейнер для значения любого типа, `.value` |
| `reactive(obj)` | глубокий реактивный прокси объекта (не примитивы) |
| `shallowRef/shallowReactive` | только верхний уровень (производительность больших структур) |
| `toRef/toRefs` | связь с полями реактивного объекта |
| `readonly` | защита от записи |
| `toRaw`, `markRaw` | доступ к исходному объекту / отключение реактивности |
| `isRef`, `unref`, `toValue` | вспомогательные |
| `customRef` | своя логика (debounce ref) |

`ref` vs `reactive`: рекомендуется **`ref` по умолчанию** — работает с примитивами, можно заменить значение целиком, нет потери реактивности при передаче; `reactive` удобен для локального объекта состояния, но теряется при деструктуризации и замене всей ссылки.

В шаблоне ref верхнего уровня разворачивается автоматически (`{{ count }}`); внутри вложенных объектов — только если ref лежит в `reactive`.

## Нюансы и подводные камни

- `ref` внутри обычного объекта (не reactive) не разворачивается: нужен `.value`.
- `reactive` нельзя полностью заменить: `state = {...}` теряет реактивность (используйте `Object.assign` или `ref`).
- Прокси не идентичен исходному объекту: `state !== toRaw(state)`.
- Большие неизменяемые структуры (карты, графики, экземпляры классов) — `shallowRef`/`markRaw`.
- Реактивность работает только для объектов, созданных до чтения; добавление новых свойств отслеживается (в отличие от Vue 2).

## Практика

1. Сравните поведение `ref`/`reactive` при деструктуризации и замене.
2. Оберните большую структуру в `shallowRef` и обновляйте заменой.
3. Реализуйте `debouncedRef` через `customRef`.

## Вопросы с ответами

> [!question]- Чем `ref` отличается от `reactive`?
> `ref` — контейнер значения с `.value` (любые типы), `reactive` — прокси объекта без `.value`, но с ограничениями (нельзя примитивы, теряется при замене).

> [!question]- Зачем `toRefs`?
> Чтобы деструктурировать реактивный объект без потери реактивности.

> [!question]- Когда `shallowRef`?
> Для больших структур, где нужна реактивность только при замене всего значения.

## Связанные темы

- [[N:3ea3310486798159b099d64b024d840d]]
- [[N:3ea3310486798127b268e92751718ab6]]
