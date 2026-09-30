---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 1
status: todo
level: middle
notion_id: 3ea331048679811d86f8f287c4b108ec
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/sfc, topic/templates, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# SFC и шаблонный синтаксис

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · → [[FE 4.1.2 Директивы — v-if и v-show, v-for и key, v-bind, v-on, v-model|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Базовый вопрос по Vue: из чего состоит компонент и как работает шаблон.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**SFC (Single File Component)** — `.vue` файл с блоками `<template>`, `<script>`/`<script setup>`, `<style>`.

```vue
<script setup lang="ts">
import { ref, computed } from "vue";
const props = defineProps<{ title: string }>();
const count = ref(0);
const doubled = computed(() => count.value * 2);
const html = "<b>текст</b>";
</script>

<template>
  <section :class="{ active: count > 0 }" :style="{ color: 'red' }">
    <h2>{{ props.title }} — {{ count }} ({{ doubled }})</h2>
    <p v-html="html" />                       <!-- опасно: только доверенный HTML -->
    <button @click="count++">+1</button>
    <span>{{ count > 5 ? "много" : "мало" }}</span>
  </section>
</template>

<style scoped>
h2 { color: var(--primary); }
</style>
```

Шаблонный синтаксис:

| Конструкция | Назначение |
|---|---|
| `{{ expr }}` | интерполяция текста (экранируется) |
| `:attr="expr"` (`v-bind`) | динамический атрибут/prop |
| `@event="handler"` (`v-on`) | обработчик события |
| `v-model` | двусторонняя привязка |
| `#slot` (`v-slot`) | слоты |
| Выражения | одно JS-выражение без инструкций; доступ к ограниченному набору глобалей |

Шаблон **компилируется** в render-функции (на этапе сборки), при этом статические части поднимаются и помечаются для оптимизации (patch flags, hoisting, block tree).

`<style scoped>` изолирует стили (атрибут `data-v-*`), `<style module>` — CSS Modules, `v-bind()` в CSS привязывает стили к состоянию.

Несколько корней у шаблона поддерживаются (Vue 3, fragments).

## Нюансы и подводные камни

- `v-html` с пользовательскими данными — XSS.
- В шаблоне доступны только объявленные привязки `<script setup>` автоматически; в Options API — через `this`.
- Сложную логику выносите из шаблона в `computed`/функции.
- Вызов методов в шаблоне выполняется при каждом рендере — используйте `computed` для дорогих операций.
- Регистр атрибутов в DOM-шаблонах (не SFC) нечувствителен.

## Практика

1. Создайте компонент с интерполяцией, привязками, обработчиками и scoped-стилями.
2. Посмотрите скомпилированный render в Vue SFC Playground.
3. Замените вызов метода в шаблоне на `computed`.

## Вопросы с ответами

> [!question]- Что такое SFC?
> Файл `.vue`, объединяющий шаблон, логику и стили компонента.

> [!question]- Что делает scoped?
> Ограничивает стили текущим компонентом, добавляя атрибут `data-v-*` к элементам и селекторам.

## Связанные темы

- [[N:cf701e59e7894adfb9428fd9c9678d93]]
- [[N:3ea3310486798105b2c2db4cab84b0c5]]
