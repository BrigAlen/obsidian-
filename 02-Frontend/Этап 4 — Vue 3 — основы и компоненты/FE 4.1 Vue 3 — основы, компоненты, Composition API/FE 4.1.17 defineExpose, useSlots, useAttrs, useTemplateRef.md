---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 17
status: todo
level: middle
notion_id: 3ea33104867981379a3acac7a6ac0899
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/script-setup, topic/api, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# defineExpose, useSlots, useAttrs, useTemplateRef

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.16 Template refs и nextTick|Предыдущая]] · → [[FE 4.1.18 Динамические компоненты — component —is|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Вспомогательные API `<script setup>`: как получить слоты, атрибуты и открыть публичный интерфейс компонента.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```vue
<script setup lang="ts">
import { useSlots, useAttrs, useTemplateRef, getCurrentInstance, useId } from "vue";

const slots = useSlots();                    // { default?, header?, ... }
const attrs = useAttrs();                    // fallthrough-атрибуты
const hasHeader = !!slots.header;
const id = useId();                          // стабильный уникальный id (SSR-safe) для label/aria

const el = useTemplateRef<HTMLDivElement>("root");

function focus() { el.value?.focus(); }
function validate(): boolean { /* ... */ return true; }
defineExpose({ focus, validate });          // публичный API для template ref родителя
</script>

<template>
  <div ref="root" tabindex="-1"><slot /><slot name="header" v-if="hasHeader" /></div>
</template>
```

Родитель:

```vue
<script setup lang="ts">
import type { ComponentExposed } from "vue-component-type-helpers";
const form = useTemplateRef<InstanceType<typeof ChildForm>>("form");
form.value?.validate();
</script>
<template><ChildForm ref="form" /></template>
```

| API | Назначение |
|---|---|
| `defineExpose` | что доступно родителю через ref |
| `useSlots`, `useAttrs` | доступ к слотам и attrs в `setup` |
| `useTemplateRef` | типобезопасный ref шаблона |
| `useId` | идентификатор для доступности |
| `useModel` | низкоуровневая версия `defineModel` |
| `getCurrentInstance` | внутренний API (избегать) |

Идея: компонент — **чёрный ящик**, публичный интерфейс = props + emits + slots + `defineExpose`. Чем меньше `expose`, тем меньше связанности.

## Нюансы и подводные камни

- `getCurrentInstance()` — внутренний API, не для прикладного кода.
- `expose` не реактивен для изменения снаружи; выставляйте методы, а не внутреннее состояние.
- `useSlots()` не реактивен на добавление слотов; используйте в шаблоне `$slots`.
- `useId` не для ключей `v-for`.

## Практика

1. Экспортируйте `open()/close()` из модального окна.
2. Свяжите `label` и `input` через `useId`.
3. Получите типы экспонируемых методов для родителя.

## Вопросы с ответами

> [!question]- Зачем `defineExpose`?
> В `<script setup>` компонент закрыт; expose открывает только выбранные методы и данные родителю.

> [!question]- Как проверить наличие слота?
> `useSlots().name` или `$slots.name` в шаблоне.

## Связанные темы

- [[N:3ea331048679812b9f59c1d0f251d6f8]]
- [[N:3ea33104867981b38c0bfd41456db1be]]
