---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 8
status: todo
level: middle
notion_id: 3ea33104867981c18a4ad4ea83878013
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/directives, topic/custom, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Кастомные директивы

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.7 watch и watchEffect|Предыдущая]] · → [[FE 4.1.9 Потеря реактивности и частые ошибки|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




















> [!info] Зачем это на собесе
> Когда нужна директива и как она работает с DOM в хуках жизненного цикла.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Директива инкапсулирует **низкоуровневый доступ к DOM** (фокус, drag, клик вне, tooltip). Логику компонентов и состояния реализуйте composables/компонентами.

```ts
// Локальная в <script setup>: переменная с префиксом v
const vFocus = { mounted: (el: HTMLElement) => el.focus() };

// Глобальная
app.directive("click-outside", {
  mounted(el, binding) {
    el._handler = (e: MouseEvent) => { if (!el.contains(e.target as Node)) binding.value(e); };
    document.addEventListener("click", el._handler);
  },
  unmounted(el) { document.removeEventListener("click", el._handler); },
});
```

```vue
<input v-focus />
<div v-click-outside="close" />
<div v-tooltip.top="'Подсказка'" />         <!-- binding.arg / binding.modifiers -->
```

Хуки: `created`, `beforeMount`, `mounted`, `beforeUpdate`, `updated`, `beforeUnmount`, `unmounted`. Аргументы: `el`, `binding` (`value`, `oldValue`, `arg`, `modifiers`, `instance`), `vnode`. Сокращённая форма: функция = `mounted` + `updated`.

Когда использовать: фокус, `click-outside`, lazy-load изображений, ресайз-наблюдатели, права доступа (`v-can`), маски ввода.

Альтернатива: composable с `useEventListener`/`onClickOutside` из VueUse и `template ref`.

## Нюансы и подводные камни

- Всегда снимайте слушатели в `unmounted`.
- Директивы не работают на компонентах с несколькими корнями (применяются к корню, `inheritAttrs`).
- В SSR нет DOM: используйте `getSSRProps`/защиту.
- Не храните состояние в `el` без необходимости — лучше `WeakMap`.

## Практика

1. Напишите `v-click-outside` с очисткой.
2. Реализуйте директиву `v-can="'orders:edit'"`, скрывающую элемент без права.
3. Сравните с `onClickOutside` из VueUse.

## Вопросы с ответами

> [!question]- Когда нужна кастомная директива?
> Когда требуется прямая работа с DOM, повторяемая для разных элементов.

> [!question]- Какие хуки есть у директивы?
> `created`, `beforeMount`, `mounted`, `beforeUpdate`, `updated`, `beforeUnmount`, `unmounted`.

## Связанные темы

- [[N:3ea33104867981b588dcc193852b1e9a]]
- [[N:3ea331048679815986d3d9f36b0a885b]]
