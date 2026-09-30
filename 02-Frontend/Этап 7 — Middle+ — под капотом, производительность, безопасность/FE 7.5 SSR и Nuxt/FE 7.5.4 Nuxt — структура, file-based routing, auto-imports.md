---
type: topic
domain: frontend
stage: 7
section: "7.5"
order: 4
status: todo
level: senior
notion_id: 3ea331048679811f968fe7af725c42d5
tags: [domain/frontend, stage/7, level/senior, topic/nuxt, topic/routing, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Nuxt: структура, file-based routing, auto-imports

↑ [[FE 7.5 SSR и Nuxt|7.5 SSR и Nuxt]] · ← [[FE 7.5.3 SSR во Vue — createSSRApp, ограничения|Предыдущая]] · → [[FE 7.5.5 Nuxt — useFetch, useAsyncData, server routes|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Nuxt — стандартный SSR-фреймворк Vue; спрашивают структуру проекта и «магию» соглашений.

## Структура

```text
├─ app/
│  ├─ pages/           # маршруты по файлам
│  ├─ components/      # авто-импорт компонентов
│  ├─ composables/     # авто-импорт composables
│  ├─ layouts/         # обёртки страниц
│  ├─ middleware/      # route middleware
│  ├─ plugins/         # плагины приложения
│  └─ app.vue
├─ server/
│  ├─ api/             # API-маршруты (/api/*)
│  ├─ routes/, middleware/, utils/
├─ public/             # статика
└─ nuxt.config.ts
```

## Маршрутизация

| Файл | URL |
|---|---|
| `pages/index.vue` | `/` |
| `pages/users/index.vue` | `/users` |
| `pages/users/[id].vue` | `/users/:id` |
| `pages/[...slug].vue` | catch-all |
| `pages/users.vue` + `users/` | родитель с `<NuxtPage />` для вложенных |

```vue
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'auth' })
const route = useRoute()
</script>
```

## Auto-imports

Компоненты из `components/`, composables из `composables/`, утилиты Vue (`ref`, `computed`) и Nuxt (`useFetch`, `useRoute`) доступны без import. Типы генерируются в `.nuxt/`.

## Режимы рендеринга по маршрутам

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    '/': { prerender: true },              // SSG
    '/blog/**': { isr: 3600 },             // ISR
    '/admin/**': { ssr: false },           // CSR (SPA)
    '/api/**': { cors: true },
  },
})
```

## Модули

`@nuxt/image`, `@nuxt/content`, `@pinia/nuxt`, `@nuxtjs/i18n`, `nuxt-auth-utils`, `@vueuse/nuxt`.

## Nitro

Серверный движок Nuxt: универсальный, деплой на Node, serverless, edge (Cloudflare, Vercel).

## Вопросы с ответами

> [!question]- Как в Nuxt задать разные режимы рендеринга?
> Через `routeRules` в `nuxt.config.ts`: prerender, isr, swr, ssr: false для групп маршрутов.

> [!question]- Недостатки auto-imports?
> Меньше явности, IDE и линтер нужны типы `.nuxt`; при конфликте имён сложнее понять источник.
