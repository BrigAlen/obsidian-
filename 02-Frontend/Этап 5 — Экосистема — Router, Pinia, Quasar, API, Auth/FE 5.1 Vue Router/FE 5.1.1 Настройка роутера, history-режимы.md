---
type: topic
domain: frontend
stage: 5
section: "5.1"
order: 1
status: todo
level: middle
notion_id: 3ea331048679815f8ab2fd34e863ccd4
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/router, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Настройка роутера, history-режимы

↑ [[FE 5.1 Vue Router|5.1 Vue Router]] · → [[FE 5.1.2 Динамические и вложенные маршруты|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Базовый вопрос: как устроен SPA-роутинг и чем `createWebHistory` отличается от hash-режима.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
import { createRouter, createWebHistory, createWebHashHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),      // чистые URL через History API
  routes: [
    { path: "/", name: "home", component: () => import("@/pages/HomePage.vue") },
    { path: "/:pathMatch(.*)*", name: "not-found", component: () => import("@/pages/NotFound.vue") },
  ],
  scrollBehavior: () => ({ top: 0 }),
});
app.use(router);
```

```vue
<RouterLink :to="{ name: 'order', params: { id: 1 } }" active-class="active">Заказ</RouterLink>
<RouterView v-slot="{ Component, route }"><Transition><component :is="Component" :key="route.path" /></Transition></RouterView>
```

| Режим | URL | Требования |
|---|---|---|
| `createWebHistory` | `/orders/1` | сервер должен отдавать `index.html` для всех путей (history fallback) |
| `createWebHashHistory` | `/#/orders/1` | работает без настройки сервера; хуже для SEO |
| `createMemoryHistory` | нет URL | SSR и тесты |

**History fallback**: при прямом заходе на `/orders/1` сервер не знает такого файла и вернёт 404 — нужно правило «отдать `index.html`»:

```nginx
location / { try_files $uri $uri/ /index.html; }
```

Vite dev server делает это сам. При деплое в подпапку задайте `base` (`createWebHistory("/app/")`, `base` в Vite).

Основные объекты: `useRouter()` (навигация), `useRoute()` (текущий маршрут: `params`, `query`, `hash`, `meta`, `matched`), `<RouterLink>`, `<RouterView>`.

## Нюансы и подводные камни

- Без fallback на сервере обновление страницы даёт 404.
- Catch-all маршрут должен идти последним и использовать `:pathMatch(.*)*`.
- `useRoute()` реактивен, но деструктуризация `params` теряет реактивность.
- Несоответствие `base` и реального пути ломает ассеты.
- В Hash-режиме якоря страницы конфликтуют с роутингом.

## Практика

1. Настройте роутер с 404-страницей и `RouterLink` с активными классами.
2. Настройте nginx fallback и проверьте прямой заход.
3. Поместите приложение в подпапку и настройте `base`.

## Вопросы с ответами

> [!question]- Чем history-режим отличается от hash?
> History использует чистые URL через History API и требует fallback на сервере; hash хранит путь после `#` и не нуждается в настройке сервера.

> [!question]- Почему при обновлении страницы 404?
> Сервер не знает клиентский маршрут; нужно отдавать `index.html`.

## Связанные темы

- [[N:3ea33104867981169f15c64990328a32]]
- [[N:3ea3310486798144b803e92c11aa8054]]
