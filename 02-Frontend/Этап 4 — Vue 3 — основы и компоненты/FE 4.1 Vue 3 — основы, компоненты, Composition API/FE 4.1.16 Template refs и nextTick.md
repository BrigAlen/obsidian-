---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 16
status: todo
level: middle
notion_id: 3ea331048679812b9f59c1d0f251d6f8
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/refs, topic/nexttick, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Template refs и nextTick

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.15 Атрибуты — $attrs и inheritAttrs|Предыдущая]] · → [[FE 4.1.17 defineExpose, useSlots, useAttrs, useTemplateRef|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















> [!info] Зачем это на собесе
> Доступ к DOM и «почему DOM ещё не обновился» — типичные вопросы.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Template ref** — ссылка на DOM-элемент или экземпляр компонента.

```vue
<script setup lang="ts">
import { ref, useTemplateRef, onMounted, nextTick } from "vue";

const input = useTemplateRef<HTMLInputElement>("nameInput");      // 3.5+ (или ref<HTMLInputElement | null>(null) с тем же именем)
const list = ref<HTMLElement | null>(null);
const rows = useTemplateRef<HTMLElement[]>("rows");                // в v-for — массив

onMounted(() => input.value?.focus());

async function add() {
  items.value.push(newItem());
  await nextTick();                                                // ждём обновления DOM
  list.value?.lastElementChild?.scrollIntoView();
}
</script>

<template>
  <input ref="nameInput" />
  <ul ref="list"><li v-for="i in items" :key="i.id" ref="rows">{{ i.title }}</li></ul>
  <ChildForm ref="form" />                                         <!-- экземпляр компонента: доступен только defineExpose -->
</template>
```

**`nextTick`**: Vue применяет изменения DOM **асинхронно и пакетно** (одна отрисовка за тик). После изменения состояния DOM ещё не обновлён; `await nextTick()` (или `nextTick(cb)`) выполняется после обновления.

```ts
count.value++;
console.log(el.value.textContent);      // старое
await nextTick();
console.log(el.value.textContent);      // новое
```

Функции-ref: `:ref="(el) => setRef(el, id)"` — для динамических случаев.

Использования: фокус, измерение размеров, прокрутка, инициализация библиотек с DOM, вызов методов дочернего компонента (`form.value?.validate()`).

## Нюансы и подводные камни

- Ref пуст (`null`) до монтирования и при `v-if` false.
- Порядок элементов в массиве refs в `v-for` не гарантирован.
- Для доступа к дочернему компоненту нужен `defineExpose`.
- Злоупотребление refs вместо данных/событий делает код императивным.
- Изменение состояния и чтение DOM в одном тике даёт устаревшие значения.

## Практика

1. Фокусируйте поле после появления через `nextTick`.
2. Прокрутите список к добавленному элементу.
3. Вызовите `validate()` дочерней формы через ref.

## Вопросы с ответами

> [!question]- Зачем `nextTick`?
> Дождаться применения отложенных обновлений DOM после изменения состояния.

> [!question]- Когда template ref доступен?
> После монтирования (`onMounted`) и пока элемент существует.

## Связанные темы

- [[N:3ea33104867981d4b22bd2fb85d16222]]
- [[N:3ea33104867981379a3acac7a6ac0899]]
