---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 11
status: todo
level: middle
notion_id: 3ea33104867981298ee7da62c03689a1
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/components, topic/props, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Props и emits, однонаправленный поток данных

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.10 Жизненный цикл компонента|Предыдущая]] · → [[FE 4.1.12 v-model на компонентах и defineModel|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




















> [!info] Зачем это на собесе
> Базовый принцип: данные вниз (props), события вверх (emits). Нарушение приводит к трудноотлаживаемому коду.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```vue
<!-- Child.vue -->
<script setup lang="ts">
interface Props { order: Order; readonly?: boolean; size?: "sm" | "md" }
const props = withDefaults(defineProps<Props>(), { readonly: false, size: "md" });
const emit = defineEmits<{ save: [order: Order]; cancel: []; "update:qty": [value: number] }>();
</script>
<template>
  <button :disabled="readonly" @click="emit('save', order)">Сохранить</button>
</template>

<!-- Parent.vue -->
<OrderCard :order="o" size="sm" @save="onSave" @cancel="close" />
```

Правила:

- **Props** передают данные родитель → потомок; потомок **не мутирует** их (предупреждение). Нужна локальная копия — `ref(props.x)` или `computed` с `get/set`.
- **Emits** — события потомок → родитель; объявляйте (`defineEmits`) для документации, типизации и корректного поведения нативных событий.
- Булевы props: наличие атрибута = `true` (`<Btn disabled />`).
- Объекты и массивы передаются по ссылке; мутация вложенных полей props технически возможна, но нарушает поток данных.
- Валидация (runtime): `type`, `required`, `default`, `validator`; в TS — интерфейс.

```ts
// Runtime-объявление
defineProps({ qty: { type: Number, required: true, validator: (v: number) => v > 0 } });

// Копия для редактирования
const draft = ref({ ...props.order });
watch(() => props.order, (o) => (draft.value = { ...o }));
```

Регистр: `defineProps({ userName })` → `:user-name` в шаблоне (kebab-case).

Когда props «слишком много» (prop drilling): `provide/inject`, стор (Pinia) или слоты.

## Нюансы и подводные камни

- Значения по умолчанию для объектов/массивов — функциями-фабриками.
- Реактивная деструктуризация props появилась в 3.5; до этого — `toRefs`.
- Не передавайте функции-коллбэки вместо событий без причины: события — идиоматичный контракт.
- Событие `update:modelValue` — основа `v-model` (см. [[N:3ea33104867981a98967d61046959e70]]).
- Пропсы, не объявленные, попадают в `$attrs` (см. [[N:3ea33104867981d4b22bd2fb85d16222]]).

## Практика

1. Сделайте карточку с типизированными props и событием `save`.
2. Реализуйте редактирование с локальной копией без мутации props.
3. Устраните prop drilling через `provide/inject`.

## Вопросы с ответами

> [!question]- Почему нельзя мутировать props?
> Данные принадлежат родителю; мутация нарушает однонаправленный поток и делает изменения непредсказуемыми.

> [!question]- Как передать данные вверх?
> Через события (`emit`), `v-model` или общий стор.

## Связанные темы

- [[N:3ea3310486798154aaa2c3a16e62edaf]]
- [[N:3ea33104867981a98967d61046959e70]]
