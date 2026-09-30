---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 26
status: todo
level: middle
notion_id: 3ea33104867981ac9e4cf9d69605a89d
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/migration, topic/vue2, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Отличия Vue 2 и Vue 3

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.25 TypeScript во Vue — типизация props, emits, ref, generic-компоненты|Предыдущая]] · → [[FE 4.1.27 Vue Test Utils — тестирование компонентов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




















> [!info] Зачем это на собесе
> Легаси на Vue 2 ещё встречается: ждут знания ключевых отличий и путей миграции.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Область | Vue 2 | Vue 3 |
|---|---|---|
| Реактивность | `Object.defineProperty` (не видит добавление/удаление свойств, индексы массивов) | `Proxy` (видит всё) |
| API | Options API | Composition API + Options |
| Переиспользование | миксины | composables |
| Корневых элементов | один | несколько (fragments) |
| TypeScript | слабая поддержка | написан на TS, отличная типизация |
| Производительность | — | быстрее (компилятор с patch flags, hoisting, tree-shaking), меньше бандл |
| `v-model` | `value`/`input`, `.sync` | `modelValue`/`update:modelValue`, несколько `v-model`, `defineModel` |
| Глобальный API | `Vue.use`, `Vue.component` | `createApp()`, изоляция экземпляров |
| Фильтры (`|`) | есть | удалены (методы/computed) |
| `$listeners`, `$children` | есть | удалены (`$attrs` включает слушатели) |
| Event bus (`$on/$off`) | есть | удалён (mitt, состояние) |
| `v-if` vs `v-for` | `v-for` приоритетнее | `v-if` приоритетнее |
| Новые возможности | — | Teleport, Suspense, `<script setup>`, Fragment, `Emits` |
| Состояние | Vuex | Pinia |
| Роутер | Vue Router 3 | Vue Router 4 |
| Сборка | Vue CLI/webpack | Vite |
| Хуки | `beforeDestroy/destroyed` | `beforeUnmount/unmounted` |
| Поддержка | EOL с декабря 2023 | актуальная |

Миграция: `@vue/compat` (режим совместимости) → постепенное устранение предупреждений; обновление экосистемы (Vuex → Pinia, Router 4, Vue Test Utils 2, UI-библиотеки); переход на Vite; переписывание миксинов на composables; затем `<script setup>` и TS.

```js
// Vue 2                                // Vue 3
new Vue({ render: h => h(App) }).$mount("#app");     createApp(App).mount("#app");
Vue.set(obj, "k", 1);                                  obj.k = 1;      // не нужен
```

## Нюансы и подводные камни

- Зависимости на Vue 2 (устаревшие UI-библиотеки) блокируют миграцию.
- Поведение `.sync`, `v-model` на компонентах и `emit` без объявления отличается.
- В Vue 3 ссылки на `this.$refs` внутри `v-for` возвращают массив без гарантии порядка.
- IE11 не поддерживается.
- Реактивность объектов создаётся прокси: сравнение `===` с исходным объектом не работает.

## Практика

1. Составьте план миграции проекта на Vue 2 с оценкой блокеров.
2. Перепишите миксин в composable.
3. Найдите использование `Vue.set`, `$listeners`, фильтров.

## Вопросы с ответами

> [!question]- Главные отличия Vue 3 от Vue 2?
> Реактивность на Proxy, Composition API, `<script setup>`, fragments, лучшая производительность и TypeScript, Pinia/Router 4/Vite.

> [!question]- Что заменило миксины?
> Composables.

## Связанные темы

- [[N:3ea33104867981faaff2c0e3e99000ab]]
- [[N:3ea3310486798105ad2acf2a9215b3fb]]
