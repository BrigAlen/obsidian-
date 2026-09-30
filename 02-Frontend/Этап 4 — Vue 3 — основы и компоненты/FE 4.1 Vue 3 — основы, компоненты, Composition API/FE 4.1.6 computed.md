---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 6
status: todo
level: middle
notion_id: 3ea3310486798127b268e92751718ab6
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/computed, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# computed

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.5 Реактивность — ref, reactive, shallowRef, toRef, toRefs|Предыдущая]] · → [[FE 4.1.7 watch и watchEffect|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Кэширование и ленивость `computed`, отличие от методов и `watch`.

## Объяснение

`computed` — производное значение: пересчитывается **лениво** и **кэшируется**, пока не изменятся зависимости.

```ts
const items = ref<Item[]>([]);
const query = ref("");
const filtered = computed(() => items.value.filter(i => i.name.includes(query.value)));
const total = computed(() => filtered.value.reduce((s, i) => s + i.price, 0));

// Writable computed
const fullName = computed({
  get: () => `${first.value} ${last.value}`,
  set: (v: string) => { [first.value, last.value] = v.split(" "); },
});
```

| | `computed` | Метод в шаблоне | `watch` |
|---|---|---|---|
| Кэш | да | нет (вызывается при каждом рендере) | — |
| Возвращает значение | да | да | нет (побочные эффекты) |
| Зависимости | автоматически | — | явные |
| Побочные эффекты | нет (должна быть чистой) | возможны | для эффектов |

Правила:

- Функция должна быть **чистой**: без мутаций, запросов, DOM.
- Возврат нового массива/объекта при каждом вычислении допустим; `computed` пересчитывается только при смене зависимостей.
- Vue 3.4+: `computed` не запускает эффекты, если значение не изменилось (по `Object.is`).
- Доступ к предыдущему значению: `computed((prev) => ...)`.

Цепочки `computed` образуют граф зависимостей; пересчёт происходит только запрошенных узлов.

## Нюансы и подводные камни

- Побочные эффекты в `computed` ломают предсказуемость.
- Изменение массива методом, не отслеживаемым (например, мутация вне Vue) не приведёт к пересчёту.
- Асинхронная логика в `computed` не поддерживается: используйте `watch`, `watchEffect` или Vue Query.
- Дорогое вычисление на большой коллекции: разделяйте на несколько `computed`.
- `computed` не выполняется, пока не прочитан.

## Практика

1. Замените метод `filteredItems()` в шаблоне на `computed` и измерьте число вычислений.
2. Реализуйте writable computed для полного имени.
3. Постройте цепочку computed: фильтр → сортировка → страница.

## Вопросы с ответами

> [!question]- Чем `computed` отличается от метода?
> `computed` кэшируется и пересчитывается только при смене зависимостей, метод выполняется при каждом рендере.

> [!question]- Можно ли делать запросы в `computed`?
> Нет: она должна быть чистой; эффекты выносите в `watch`/`watchEffect`.

## Связанные темы

- [[N:3ea33104867981d98f3ff4b0b75829f7]]
- [[N:3ea33104867981b588dcc193852b1e9a]]
