---
type: topic
domain: frontend
stage: 7
section: "7.1"
order: 7
status: todo
level: senior
notion_id: 3ea33104867981dcb491d9806abbf2b0
tags: [domain/frontend, stage/7, level/senior, topic/vue, topic/vue35, topic/vapor, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Что нового в Vue 3.3–3.5+ (Vapor Mode)

↑ [[FE 7.1 Vue под капотом|7.1 Vue под капотом]] · ← [[FE 7.1.6 Оптимизация производительности во Vue|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Показывает, что вы следите за экосистемой. Достаточно назвать ключевые фичи и мотивацию.

## 3.3

- дженерик-компоненты: `<script setup lang="ts" generic="T extends string | number">`;
- `defineSlots`, `defineOptions`;
- импорт типов в `defineProps` из внешних файлов;
- `toRef(() => props.x)` и `toValue()` для нормализации ref, getter и значения.

## 3.4

- переписанный парсер шаблонов (2× быстрее);
- `v-bind` с одинаковым именем: `:id` вместо `:id="id"`;
- `defineModel` (стабилен) для `v-model` без ручных props и emit.

```vue
<script setup lang="ts">
const model = defineModel<string>({ required: true })
</script>
<template><input v-model="model" /></template>
```

## 3.5

- **Reactive Props Destructure**: `const { title = 'x' } = defineProps<...>()` остаётся реактивным;
- `useTemplateRef()` для получения ссылок на элементы;
- `useId()` — стабильные id для SSR и a11y;
- `onWatcherCleanup`, `watch` с `pause/resume`;
- `<Teleport defer>`, ленивая гидрация (`hydrateOnVisible`, `hydrateOnIdle`);
- оптимизация реактивности: меньше памяти, быстрее для больших массивов.

## Vapor Mode

Экспериментальный режим компиляции без virtual DOM: шаблон превращается в прямые операции с DOM и реактивные подписки. Идея — производительность как у Solid и меньший размер рантайма. Совместим по API с `<script setup>`; включается на уровне компонента (`<script setup vapor>`).

## Вопросы с ответами

> [!question]- Что такое defineModel?
> Макрос для двустороннего binding: возвращает ref, синхронизированный с `modelValue` и событием `update:modelValue`. Убирает ручное объявление props и emit.

> [!question]- Зачем Vapor Mode?
> Убрать накладные расходы virtual DOM: меньше памяти и быстрее обновления, при том же синтаксисе шаблонов.
