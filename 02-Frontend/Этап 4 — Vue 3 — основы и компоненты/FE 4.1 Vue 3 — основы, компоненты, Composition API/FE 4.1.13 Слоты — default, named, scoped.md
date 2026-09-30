---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 13
status: todo
level: middle
notion_id: 3ea331048679819bb62fc73c089ec18f
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/slots, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Слоты: default, named, scoped

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.12 v-model на компонентах и defineModel|Предыдущая]] · → [[FE 4.1.14 provide и inject|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



















> [!info] Зачем это на собесе
> Слоты — основа гибких компонентов (таблицы, карточки, модалки); scoped-слоты — «render props» Vue.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Слот позволяет родителю передать разметку внутрь дочернего компонента.

```vue
<!-- Card.vue -->
<template>
  <article class="card">
    <header><slot name="header">Заголовок по умолчанию</slot></header>
    <div class="body"><slot /></div>                              <!-- default -->
    <footer><slot name="footer" :close="close" :count="items.length" /></footer>   <!-- scoped: данные вниз -->
  </article>
</template>

<!-- Использование -->
<Card>
  <template #header><h3>Заказы</h3></template>
  <p>Основное содержимое</p>
  <template #footer="{ close, count }"><button @click="close">Закрыть ({{ count }})</button></template>
</Card>
```

| Вид | Смысл |
|---|---|
| Default | безымянный `<slot />` |
| Named | `<slot name="x">` + `#x` (`v-slot:x`) |
| Scoped | слот передаёт данные родителю: `<slot :item="item">` + `#default="{ item }"` |
| Fallback | содержимое по умолчанию внутри `<slot>` |
| Динамические имена | `<template #[dynamicName]>` |
| Проверка | `$slots.header`, `useSlots()` — есть ли слот |

Пример scoped-слота в таблице:

```vue
<DataTable :rows="orders" :columns="columns">
  <template #cell-status="{ row }"><StatusBadge :value="row.status" /></template>
  <template #empty>Нет данных</template>
</DataTable>
```

Типизация слотов: `defineSlots<{ default(props: {}): any; item(props: { row: Order }): any }>()`.

Области видимости: содержимое слота компилируется в контексте **родителя** (видит его состояние), но получает данные потомка только через scoped-props.

## Нюансы и подводные камни

- Нельзя обратиться к состоянию потомка из слота без scoped-props.
- Условный рендеринг обёрток: проверьте `$slots.header` перед выводом контейнера.
- Слоты могут вызывать лишние перерендеры потомка; стабильные ссылки на данные.
- Слоты в `<script setup>`: `useSlots()`.
- Слот и `v-for`: `<slot v-for="..." />` допустим.

## Практика

1. Сделайте `Modal` со слотами header/default/footer.
2. Реализуйте `DataTable` со scoped-слотом для ячеек.
3. Добавьте типизацию `defineSlots`.

## Вопросы с ответами

> [!question]- Что такое scoped slot?
> Слот, передающий данные из компонента-потомка в контент родителя через props слота.

> [!question]- Кому принадлежит область видимости содержимого слота?
> Родителю: слот видит его переменные, но не состояние потомка без scoped-props.

## Связанные темы

- [[N:3ea33104867981a98967d61046959e70]]
- [[N:3ea331048679813dbb9aec9570420803]]
