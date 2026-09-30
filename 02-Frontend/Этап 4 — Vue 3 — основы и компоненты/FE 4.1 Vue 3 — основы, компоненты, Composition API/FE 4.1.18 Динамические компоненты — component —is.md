---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 18
status: todo
level: middle
notion_id: 3ea33104867981b38c0bfd41456db1be
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/dynamic-components, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Динамические компоненты: component :is

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.17 defineExpose, useSlots, useAttrs, useTemplateRef|Предыдущая]] · → [[FE 4.1.19 Встроенные компоненты — Transition, KeepAlive, Teleport, Suspense|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Переключение компонентов по данным: табы, визарды, рендер по схеме.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```vue
<script setup lang="ts">
import { shallowRef, markRaw, defineAsyncComponent } from "vue";
import TextField from "./TextField.vue"; import SelectField from "./SelectField.vue";

const map = { text: TextField, select: SelectField } as const;
const current = shallowRef<Component>(TextField);        // shallowRef/markRaw: компонент не должен быть глубоко реактивным
const fields = [{ type: "text", name: "a" }, { type: "select", name: "b" }];
</script>

<template>
  <component :is="current" v-bind="props" @change="onChange" />

  <!-- Рендер формы по схеме -->
  <component v-for="f in fields" :key="f.name" :is="map[f.type]" v-bind="f" v-model="model[f.name]" />

  <!-- Сохранение состояния переключаемых компонентов -->
  <KeepAlive :include="['Tab1']" :max="5"><component :is="tabs[active]" /></KeepAlive>
  <component :is="isLink ? 'a' : 'button'" :href="url" />          <!-- нативные теги -->
</template>
```

`:is` принимает: строку (имя зарегистрированного компонента или тега), сам компонент (объект/функцию).

Особенности:

- Значение компонента храните в `shallowRef` (или `markRaw`), иначе Vue создаёт реактивный прокси над определением компонента (предупреждение и лишние расходы).
- Переключение уничтожает предыдущий компонент; для сохранения состояния — `<KeepAlive>` (`activated/deactivated`).
- Атрибуты и слушатели прокидываются на текущий компонент.
- Для асинхронных вариантов — `defineAsyncComponent` (см. [[N:3ea33104867981fcb497fa1eaf2daa2e]]).

Использования: табы, динамические формы (schema-driven UI), рендер виджетов дашборда, полиморфные компоненты (`as`-prop).

## Нюансы и подводные камни

- Строка в `:is` в SFC требует регистрации компонента (глобально или `resolveComponent`).
- Без `KeepAlive` состояние формы теряется при переключении.
- Разные компоненты получают одни и те же props — лишние попадают в `$attrs` и DOM.
- Обращение к слотам динамического компонента — как обычно.

## Практика

1. Сделайте табы с `component :is` и `KeepAlive`.
2. Отрендерите форму по JSON-схеме полей.
3. Реализуйте полиморфный `Btn` (`a`/`button`/`RouterLink`).

## Вопросы с ответами

> [!question]- Что делает `<component :is>`?
> Динамически рендерит компонент или тег по значению выражения.

> [!question]- Как сохранить состояние при переключении?
> Обернуть в `<KeepAlive>`.

## Связанные темы

- [[N:3ea33104867981379a3acac7a6ac0899]]
- [[N:3ea33104867981d5912bd2c38599765c]]
