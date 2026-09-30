---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 2
status: todo
level: middle
notion_id: 3ea3310486798105b2c2db4cab84b0c5
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/directives, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Директивы: v-if и v-show, v-for и key, v-bind, v-on, v-model

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.1 SFC и шаблонный синтаксис|Предыдущая]] · → [[FE 4.1.3 Options API и Composition API|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




















> [!info] Зачем это на собесе
> `v-if` против `v-show`, зачем `key` и почему нельзя `v-if` вместе с `v-for` — вопросы каждого собеседования по Vue.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Директива | Поведение |
|---|---|
| `v-if` / `v-else-if` / `v-else` | условный рендеринг: элемент создаётся/уничтожается |
| `v-show` | переключает `display: none`, элемент остаётся в DOM |
| `v-for` | список: `item in items`, `(item, i) in items`, объекты, диапазоны |
| `v-bind` (`:`) | привязка атрибутов/props; `:class`, `:style`, `v-bind="obj"` |
| `v-on` (`@`) | события; модификаторы `.prevent`, `.stop`, `.once`, `.self`, `.capture`, `.passive`, `.enter` |
| `v-model` | синхронизация value + input; модификаторы `.trim`, `.number`, `.lazy` |
| `v-once`, `v-memo`, `v-pre`, `v-cloak` | оптимизации и служебные |

`v-if` vs `v-show`: `v-if` дороже при переключении (создание), но не тратит ресурсы, когда скрыт (ленивый); `v-show` дешёвый при частом переключении, но рендерится сразу.

```vue
<template>
  <p v-if="loading">Загрузка...</p>
  <ul v-else-if="orders.length">
    <li v-for="order in orders" :key="order.id" @click.stop="open(order.id)">{{ order.number }}</li>
  </ul>
  <p v-else>Нет данных</p>

  <input v-model.trim="query" @keyup.enter="search">
  <li v-for="(value, key, index) in obj" :key="key" />
  <span v-for="n in 5" :key="n">{{ n }}</span>
  <button :disabled="!valid" :class="[base, { active }]">OK</button>
</template>
```

**`key`** позволяет Vue сопоставлять элементы между рендерами и переиспользовать/перемещать их корректно. Ключ должен быть **стабильным и уникальным** (id), а не индексом, если список меняется (вставка, сортировка, удаление): иначе состояние (фокус, ввод, анимации) «прилипает» не к тем элементам.

`v-if` и `v-for` на одном элементе: во Vue 3 `v-if` имеет приоритет и не видит переменную цикла — используйте `computed` (фильтрация) или `<template v-for>` с `v-if` внутри.

## Нюансы и подводные камни

- `v-for` без `key` или с индексом при динамическом списке — баги с состоянием.
- `key` можно использовать и для принудительного пересоздания компонента.
- `v-show` не работает с `<template>`.
- `v-model` на `number` даёт строку без `.number`.
- Обработчики в шаблоне: `@click="fn"` (ссылка) и `@click="fn(arg)"` (вызов при клике).

## Практика

1. Сделайте список с сортировкой и убедитесь, что `key = id` сохраняет состояние инпутов.
2. Сравните `v-if` и `v-show` по числу создаваемых узлов.
3. Отфильтруйте список через `computed` вместо `v-if` внутри `v-for`.

## Вопросы с ответами

> [!question]- Чем `v-if` отличается от `v-show`?
> `v-if` создаёт и уничтожает элемент, `v-show` только переключает `display`.

> [!question]- Зачем нужен `key` в `v-for`?
> Для корректного сопоставления и переиспользования элементов при изменении списка.

> [!question]- Можно ли `v-if` и `v-for` на одном элементе?
> Не рекомендуется: `v-if` выполняется раньше и не видит переменную цикла; используйте `computed` или вложенный `<template>`.

## Связанные темы

- [[N:3ea331048679811d86f8f287c4b108ec]]
- [[N:3ea33104867981d08201e00f96e273a7]]
