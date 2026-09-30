---
type: topic
domain: frontend
stage: 7
section: "7.5"
order: 2
status: todo
level: senior
notion_id: 3ea33104867981fd92fff7a3c0590395
tags: [domain/frontend, stage/7, level/senior, topic/ssr, topic/hydration, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Гидрация и hydration mismatch

↑ [[FE 7.5 SSR и Nuxt|7.5 SSR и Nuxt]] · ← [[FE 7.5.1 CSR, SSR, SSG, ISR — как работают и когда что выбирать|Предыдущая]] · → [[FE 7.5.3 SSR во Vue — createSSRApp, ограничения|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Hydration mismatch — самая частая проблема SSR; важно уметь объяснить причину и починить.

## Гидрация

Сервер отдаёт HTML, клиент запускает то же приложение и **сопоставляет** vnode с существующим DOM, не пересоздавая его, добавляет обработчики и реактивность.

## Mismatch

Ошибка возникает, когда дерево на клиенте отличается от серверного HTML.

Частые причины:

| Причина | Пример |
|---|---|
| Данные, зависящие от среды | `window`, `localStorage`, ширина экрана |
| Время и случайность | `new Date()`, `Math.random()`, `Date.now()` |
| Таймзона и локаль | разный формат даты на сервере и клиенте |
| Невалидный HTML | `<p>` внутри `<p>`, `<div>` в `<p>`, браузер меняет структуру |
| Разные данные | сервер и клиент получили разные ответы API |
| Расширения браузера | вставляют узлы в DOM |

## Как чинить

```vue
<script setup lang="ts">
const now = ref('')
onMounted(() => { now.value = new Date().toLocaleString() })   // только на клиенте
</script>

<template>
  <ClientOnly>              <!-- Nuxt -->
    <ChartWidget />
    <template #fallback><Skeleton /></template>
  </ClientOnly>
</template>
```

- состояние, зависящее от браузера, инициализировать в `onMounted`;
- передавать серверное состояние клиенту (Nuxt `useState`, Pinia `state` в `window.__INITIAL_STATE__`);
- время и локаль форматировать в одной таймзоне;
- `useId()` для стабильных идентификаторов;
- `data-allow-mismatch` (Vue 3.5) точечно подавляет предупреждение.

## Ленивая гидрация (Vue 3.5)

```ts
const Comments = defineAsyncComponent({
  loader: () => import('./Comments.vue'),
  hydrate: hydrateOnVisible(),   // гидрируем, когда блок попал в viewport
})
```

Также `hydrateOnIdle`, `hydrateOnInteraction`, `hydrateOnMediaQuery`.

## Стоимость

Гидрация выполняет весь JS ещё раз: «uncanny valley» — страница видна, но не отвечает. Уменьшают бандл, ленивая гидрация, острова.

## Вопросы с ответами

> [!question]- Что такое hydration mismatch?
> Расхождение между серверным HTML и тем, что рендерит клиент. Vue выдаёт предупреждение, а иногда пересоздаёт узлы, что даёт мигание и баги.

> [!question]- Как безопасно использовать window в SSR?
> Только на клиенте: `onMounted`, проверки `import.meta.client` / `typeof window`, компонент `ClientOnly`.
