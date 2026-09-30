---
type: topic
domain: frontend
stage: 7
section: "7.5"
order: 3
status: todo
level: senior
notion_id: 3ea331048679811ca64ec0197d626ed1
tags: [domain/frontend, stage/7, level/senior, topic/ssr, topic/vue, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# SSR во Vue: createSSRApp, ограничения

↑ [[FE 7.5 SSR и Nuxt|7.5 SSR и Nuxt]] · ← [[FE 7.5.2 Гидрация и hydration mismatch|Предыдущая]] · → [[FE 7.5.4 Nuxt — структура, file-based routing, auto-imports|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Показывает понимание, что происходит «под капотом» Nuxt.

## Схема

Один код приложения запускается на сервере и в браузере. **Фабрика** приложения создаёт новый экземпляр на каждый запрос.

```ts
// app.ts (общий)
import { createSSRApp } from 'vue'
import { createRouter, createMemoryHistory, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'

export function createApp() {
  const app = createSSRApp(App)
  const pinia = createPinia()
  const router = createRouter({
    history: import.meta.env.SSR ? createMemoryHistory() : createWebHistory(),
    routes,
  })
  app.use(pinia).use(router)
  return { app, router, pinia }
}
```

```ts
// entry-server.ts
import { renderToString } from 'vue/server-renderer'
export async function render(url: string) {
  const { app, router, pinia } = createApp()
  await router.push(url)
  await router.isReady()
  const html = await renderToString(app)
  return { html, state: pinia.state.value }
}
```

```ts
// entry-client.ts
const { app, router, pinia } = createApp()
pinia.state.value = window.__INITIAL_STATE__
router.isReady().then(() => app.mount('#app'))   // гидрация
```

## Ограничения

- нет `window`, `document`, `localStorage` на сервере;
- **не хранить состояние в модульных переменных** — оно общее для всех запросов (утечка данных между пользователями). Создавать на каждый запрос;
- хуки `mounted`, `updated` и `watch` с побочными эффектами не выполняются на сервере: только `setup`, `beforeCreate`, `created`;
- сторонние библиотеки, обращающиеся к DOM при импорте;
- директивы: для SSR нужны серверные реализации (`getSSRProps`);
- утечки памяти: на сервере нет размонтирования, подписки в `setup` не очищаются.

## Инструменты

`vite-plugin-ssr` / Vike, Nuxt, Quasar SSR, `@vue/server-renderer` (`renderToString`, `renderToNodeStream`, `renderToWebStream`).

## Вопросы с ответами

> [!question]- Почему нельзя держать состояние в глобальной переменной при SSR?
> Процесс сервера один и обслуживает многих пользователей: глобальное состояние будет общим и приведёт к утечке данных между запросами.

> [!question]- Какие хуки жизненного цикла выполняются на сервере?
> Только `setup` (и `beforeCreate`, `created` в Options API). `onMounted` и далее — только в браузере.
