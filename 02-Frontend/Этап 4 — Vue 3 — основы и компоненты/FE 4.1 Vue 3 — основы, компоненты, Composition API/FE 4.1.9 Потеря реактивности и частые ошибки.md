---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 9
status: todo
level: middle
notion_id: 3ea331048679815986d3d9f36b0a885b
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/reactivity, topic/pitfalls, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Потеря реактивности и частые ошибки

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.8 Кастомные директивы|Предыдущая]] · → [[FE 4.1.10 Жизненный цикл компонента|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

















> [!info] Зачем это на собесе
> «Почему компонент не обновляется?» — ждут перечня типовых причин.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Ситуация | Почему теряется | Решение |
|---|---|---|
| Деструктуризация `reactive`: `const { a } = state` | получаем примитив | `toRefs(state)` / `toRef` |
| Деструктуризация props (до 3.5) | то же | `toRefs(props)` или `() => props.x`; в 3.5 — реактивная деструктуризация |
| Замена всего `reactive`: `state = {...}` | переменная указывает на другой объект | `Object.assign(state, next)` или `ref` |
| Передача значения `ref.value` в composable | копия | передавать `ref` или геттер (`toValue`) |
| `ref` внутри обычного объекта | не разворачивается | `.value` или `reactive` |
| Вынос реактивного в обычную переменную/класс | вне отслеживания | оставлять в реактивной структуре |
| `watch(state.prop)` | не реактивный источник | `watch(() => state.prop)` |
| `markRaw`/`toRaw` | намеренно отключено | использовать сознательно |
| Изменение вне Vue (сторонняя библиотека) | Vue не знает | `triggerRef`, копия/замена |
| `ref` в `Map`/`Set` | ограниченно | использовать реактивные коллекции |
| Асинхронность после `await` в `watchEffect` | зависимости не собираются | читать до `await` |

```ts
// Ошибка
const { count } = useCounter();   // count — число, если composable вернул reactive-объект
// Правильно: composable возвращает refs
function useCounter() { const count = ref(0); return { count, inc: () => count.value++ }; }

// Приём: принимать ref/геттер/значение
function useTitle(source: MaybeRefOrGetter<string>) { watchEffect(() => (document.title = toValue(source))); }
```

Другие типовые ошибки:

- Мутация props (`props.x = 1`) — предупреждение; эмитить событие или использовать `defineModel`.
- Отсутствие `key` в списках.
- Тяжёлые вычисления в шаблоне, а не в `computed`.
- Забытая очистка таймеров/слушателей.
- Обращение к DOM до `onMounted` и без `nextTick` после изменения данных.
- Реактивный объект с тяжёлыми не-реактивными данными (карты, инстансы) — `markRaw`.

## Нюансы и подводные камни

- Проверяйте `isRef`, `isReactive`, Vue DevTools (подсветка обновлений).
- Разворачивание `ref` в шаблоне работает только для верхнего уровня.
- Реактивность массива: методы `push/splice` и индексная запись работают во Vue 3.

## Практика

1. Воспроизведите 5 случаев потери реактивности и исправьте.
2. Перепишите composable, принимающий `MaybeRefOrGetter`.
3. Найдите мутацию props в своём проекте.

## Вопросы с ответами

> [!question]- Почему после деструктуризации `reactive` компонент не обновляется?
> Мы получаем копию значения, отвязанную от прокси; нужны `toRefs`/`toRef`.

> [!question]- Как передать реактивное значение в composable?
> Как `ref`, геттер или `MaybeRefOrGetter` и читать через `toValue`.

## Связанные темы

- [[N:3ea33104867981c18a4ad4ea83878013]]
- [[N:3ea3310486798154aaa2c3a16e62edaf]]
