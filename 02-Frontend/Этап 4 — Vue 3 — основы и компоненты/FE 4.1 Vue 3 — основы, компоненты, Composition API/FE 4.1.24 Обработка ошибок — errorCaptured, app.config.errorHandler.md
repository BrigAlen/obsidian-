---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 24
status: todo
level: middle
notion_id: 3ea3310486798126a148ed51c5b0b006
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/errors, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Обработка ошибок: errorCaptured, app.config.errorHandler

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.23 Плагины Vue|Предыдущая]] · → [[FE 4.1.25 TypeScript во Vue — типизация props, emits, ref, generic-компоненты|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

















> [!info] Зачем это на собесе
> Как не уронить приложение из-за ошибки в одном компоненте и собрать данные об ошибках.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Уровни обработки:

| Уровень | Механизм |
|---|---|
| Локальный | `try/catch` в обработчиках и `async`-функциях |
| Компонентная граница | `onErrorCaptured` (ловит ошибки потомков: рендер, хуки, watchers, обработчики) |
| Глобальный | `app.config.errorHandler` |
| Предупреждения | `app.config.warnHandler` (dev) |
| Вне Vue | `window.addEventListener("error" / "unhandledrejection")` |
| Роутер | `router.onError` |
| Запросы | обработка в API-клиенте/интерсепторах, `onError` в Vue Query |

```vue
<!-- ErrorBoundary.vue -->
<script setup lang="ts">
const error = ref<Error | null>(null);
onErrorCaptured((err, instance, info) => {
  error.value = err as Error;
  report(err, { info, component: instance?.$options.name });
  return false;                              // остановить дальнейшее всплытие
});
const reset = () => (error.value = null);
</script>
<template>
  <slot v-if="!error" />
  <div v-else role="alert"><p>Что-то пошло не так</p><button @click="reset">Повторить</button></div>
</template>
```

```ts
// main.ts
app.config.errorHandler = (err, instance, info) => { Sentry.captureException(err, { extra: { info } }); };
window.addEventListener("unhandledrejection", (e) => Sentry.captureException(e.reason));
```

Практики:

- **Error boundary** вокруг крупных блоков (страница, виджет), чтобы сбой не «ронял» всё приложение.
- Понятные сообщения пользователю и кнопка «Повторить»; технические детали — в логи.
- Логирование в Sentry/аналог с контекстом (пользователь, маршрут, версия, breadcrumbs), source maps.
- Разделять ошибки: ожидаемые (валидация, 4xx) обрабатывать локально, неожиданные — глобально.
- Асинхронные ошибки в обработчиках событий Vue перехватываются глобальным обработчиком; вне Vue — нет.

## Нюансы и подводные камни

- `errorCaptured` не ловит ошибки в самом компоненте-границе и в асинхронном коде вне Vue.
- Возврат `false` в `errorCaptured` останавливает распространение.
- `unhandledrejection` для промисов вне компонентов.
- Не глотайте ошибки: минимум — логирование.

## Практика

1. Сделайте `ErrorBoundary` и оберните им страницы.
2. Настройте отправку ошибок в Sentry с source maps.
3. Смоделируйте ошибку рендера и проверьте поведение.

## Вопросы с ответами

> [!question]- Как ловить ошибки в компонентах-потомках?
> `onErrorCaptured` в родителе (граница ошибок) и глобально `app.config.errorHandler`.

> [!question]- Что делает `return false` в `errorCaptured`?
> Останавливает дальнейшее всплытие ошибки к родителям и глобальному обработчику.

## Связанные темы

- [[N:3ea33104867981c1ae13c70ac05504c1]]
- [[N:3ea33104867981faaff2c0e3e99000ab]]
