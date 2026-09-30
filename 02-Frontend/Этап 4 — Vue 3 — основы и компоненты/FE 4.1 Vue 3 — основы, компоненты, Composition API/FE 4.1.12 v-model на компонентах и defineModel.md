---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 12
status: todo
level: middle
notion_id: 3ea33104867981a98967d61046959e70
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/v-model, topic/defineModel, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# v-model на компонентах и defineModel

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.11 Props и emits, однонаправленный поток данных|Предыдущая]] · → [[FE 4.1.13 Слоты — default, named, scoped|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Как реализуется двусторонняя привязка на компонентах и что упростил `defineModel`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`v-model` на компоненте — сахар: prop `modelValue` + событие `update:modelValue`.

```vue
<!-- Ручная реализация -->
<script setup>
const props = defineProps<{ modelValue: string }>();
const emit = defineEmits<{ "update:modelValue": [v: string] }>();
</script>
<template><input :value="modelValue" @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)" /></template>

<!-- defineModel (3.4+): ref, синхронизированный с родителем -->
<script setup lang="ts">
const model = defineModel<string>({ default: "" });                 // v-model
const qty = defineModel<number>("qty", { required: true });         // v-model:qty
const [text, mods] = defineModel<string, "trim" | "upper">({
  set(v) { return mods.trim ? v.trim() : v; },                      // модификаторы v-model
});
</script>
<template><input v-model="model" /><button @click="qty++">+</button></template>
```

```vue
<SearchInput v-model="query" />
<Stepper v-model:qty="count" v-model:unit="unit" />
<TextField v-model.trim="name" />
```

| Особенность | Описание |
|---|---|
| Несколько `v-model` | по аргументу: `v-model:title`, `v-model:size` |
| Модификаторы | `.trim`, `.number`, свои (`modelModifiers`) |
| `defineModel` | возвращает `ref`: запись = `emit` + локальная копия при отсутствии родителя |
| Native `<input v-model>` | value + input (textarea — input, checkbox — change/`checked`, select — change) |

Сложные поля: `v-model` для объекта — эмитьте новый объект (иммутабельно), а не мутируйте.

## Нюансы и подводные камни

- Нельзя привязать `v-model` к prop потомка напрямую (`v-model="props.x"`).
- В Vue 2 было `value/input` (и `.sync`): миграция на `modelValue/update:modelValue`.
- Составные компоненты форм с `v-model` должны корректно работать с `null/undefined`.
- Для `<input v-model>` с IME (ввод на CJK) обновление происходит после завершения композиции.

## Практика

1. Сделайте компонент `TextField` с `defineModel`, поддерживающий `.trim`.
2. Реализуйте `Stepper` с двумя `v-model`.
3. Перепишите старый компонент с ручным `modelValue` на `defineModel`.

## Вопросы с ответами

> [!question]- Как работает `v-model` на компоненте?
> Передаёт prop `modelValue` и слушает событие `update:modelValue`.

> [!question]- Что упростил `defineModel`?
> Вместо пары props+emit возвращает `ref`, который синхронизируется с родителем.

## Связанные темы

- [[N:3ea33104867981298ee7da62c03689a1]]
- [[N:3ea331048679819bb62fc73c089ec18f]]
