---
type: topic
domain: frontend
stage: 7
section: "7.5"
order: 6
status: todo
level: senior
notion_id: 3ea33104867981ca8bdfecda4dc20038
tags: [domain/frontend, stage/7, level/senior, topic/quasar, topic/ssr, topic/pwa, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# SSR в Quasar

↑ [[FE 7.5 SSR и Nuxt|7.5 SSR и Nuxt]] · ← [[FE 7.5.5 Nuxt — useFetch, useAsyncData, server routes|Предыдущая]] · → [[FE 7.5.7 SSR глубже — streaming, кэширование и edge rendering|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Для стека Vue + Quasar: как получить SSR и какие отличия от Nuxt.

## Режимы Quasar

Quasar CLI умеет собирать SPA, **SSR**, PWA, SSR + PWA, Electron, Capacitor, BEX из одной кодовой базы.

```sh
quasar mode add ssr
quasar dev -m ssr
quasar build -m ssr
```

## Как работает SSR-режим

- поверх Vue SSR и Vite; сервер на **Express** (или Fastify) в `src-ssr/`;
- точки входа: `src/boot`-файлы с флагом `server`/`client`, `preFetch` для загрузки данных;
- **PWA-режим** можно добавить к SSR: после первой загрузки работает как SPA/PWA.

```ts
// src-ssr/server.ts
export const listenResult = listen({ port })
export const handler = ssrMiddleware(({ app, resolve, render, serve }) => {
  app.get(resolve.urlPath('*'), render)
})
```

## preFetch

```ts
export default defineComponent({
  preFetch({ store, currentRoute, redirect }) {
    return store.dispatch('user/load', currentRoute.params.id)
  },
})
```

Хук выполняется на сервере перед рендером и на клиенте перед переходом (кроме первой загрузки).

## Особенности и подводные камни

- компоненты Quasar SSR-совместимы, но `Platform`, `Screen`, `Dark`, `Cookies` требуют настройки с SSR-контекстом;
- `Cookies.parseSSR(ssrContext)`, `useMeta` для title и meta-тегов;
- код с `window` — в `boot` с `client`-режимом;
- состояние Pinia передаётся клиенту автоматически (`window.__INITIAL_STATE__`).

## Когда что

| Задача | Выбор |
|---|---|
| Админка с Quasar-компонентами | SPA |
| Публичный сайт с SEO на Quasar | SSR-режим |
| Публичный сайт, нужны острова, ISR, серверные роуты, ecosystem модулей | Nuxt (Quasar можно подключить модулем) |

## Вопросы с ответами

> [!question]- Как в Quasar загружать данные при SSR?
> Через `preFetch` в компоненте страницы или в роуте: на сервере он выполняется до рендера, состояние сохраняется в Pinia и передаётся клиенту.

> [!question]- Чем Quasar SSR отличается от Nuxt?
> Quasar даёт SSR как один из режимов сборки и требует больше ручной настройки; Nuxt — SSR-first фреймворк с готовыми data-fetching, routeRules, модулями.
