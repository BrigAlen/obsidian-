---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 15
status: todo
level: middle
notion_id: 3ea33104867981d4b22bd2fb85d16222
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/attrs, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Атрибуты: $attrs и inheritAttrs

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.14 provide и inject|Предыдущая]] · → [[FE 4.1.16 Template refs и nextTick|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






















> [!info] Зачем это на собесе
> Как проксировать атрибуты и события через обёртки над нативными элементами и UI-компонентами.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Fallthrough attributes**: атрибуты и обработчики, переданные компоненту, но не объявленные как `props`/`emits`, автоматически применяются к корневому элементу (`class`, `style` — объединяются).

```vue
<!-- MyInput.vue: корень — label, а нативный input нужно получить атрибуты -->
<script setup>
defineOptions({ inheritAttrs: false });          // отключить автопрокидывание на корень
const attrs = useAttrs();
</script>
<template>
  <label class="field">
    <span>{{ label }}</span>
    <input v-bind="$attrs" />                     <!-- placeholder, type, @focus, class... попадают на input -->
  </label>
</template>

<MyInput label="Имя" placeholder="Введите" type="text" @focus="log" class="wide" />
```

| Понятие | Описание |
|---|---|
| `$attrs` / `useAttrs()` | неobъявленные props + атрибуты + обработчики событий (в Vue 3 `class`, `style` и слушатели входят в `$attrs`) |
| `inheritAttrs: false` | отключает автоприменение к корню |
| `v-bind="$attrs"` | ручное проксирование на нужный элемент |
| Несколько корней | нет автопрокидывания: нужно явно `v-bind="$attrs"`, иначе предупреждение |

Применение: **обёртки над нативными и UI-библиотечными компонентами** (кастомизация Quasar `QInput` с сохранением всех его props и слотов).

```vue
<q-input v-bind="{ ...$attrs, ...defaults }">
  <template v-for="(_, slot) in $slots" #[slot]="scope"><slot :name="slot" v-bind="scope ?? {}" /></template>
</q-input>
```

Vue 3 отличия от Vue 2: `$listeners` удалён (слушатели внутри `$attrs`), `class`/`style` тоже.

## Нюансы и подводные камни

- `$attrs` не реактивен для `watch` в Options API (используйте `onUpdated`) — в Composition API `useAttrs()` даёт актуальные значения, но не отслеживается напрямую.
- Порядок слияния: `v-bind="$attrs"` до/после других атрибутов определяет приоритет.
- Не забывайте прокидывать слоты при обёртке.
- Неявное применение атрибутов на корень может быть неожиданным.

## Практика

1. Сделайте обёртку `BaseInput`, проксирующую атрибуты и события на `<input>`.
2. Оберните Quasar `q-input` с общими настройками и прокидыванием слотов.
3. Проверьте слияние `class` и `style`.

## Вопросы с ответами

> [!question]- Что такое fallthrough attributes?
> Атрибуты/события, не объявленные как props/emits, которые автоматически применяются к корневому элементу компонента.

> [!question]- Зачем `inheritAttrs: false`?
> Чтобы отправить `$attrs` на другой внутренний элемент, а не на корень.

## Связанные темы

- [[N:3ea331048679813dbb9aec9570420803]]
- [[N:3ea331048679812b9f59c1d0f251d6f8]]
