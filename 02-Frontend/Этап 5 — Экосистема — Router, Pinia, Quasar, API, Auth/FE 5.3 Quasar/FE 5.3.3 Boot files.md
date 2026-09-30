---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981d89554c287a6494d1c
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/boot, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Boot files

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.2 Структура проекта и quasar.config|Предыдущая]] · → [[FE 5.3.4 Layout — QLayout, QHeader, QDrawer, QPage|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Boot-файлы — механизм инициализации приложения (Axios, i18n, аутентификация).

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Boot-файл — модуль, выполняемый **до создания корневого компонента** и получающий контекст приложения. Регистрируется в `quasar.config` → `boot: [...]`, выполняется по порядку.

```ts
// src/boot/axios.ts
import { boot } from "quasar/wrappers";
import axios, { type AxiosInstance } from "axios";

declare module "vue" { interface ComponentCustomProperties { $api: AxiosInstance } }
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL });

export default boot(({ app, router, store, urlPath, redirect }) => {
  app.config.globalProperties.$api = api;
  app.provide("api", api);
  api.interceptors.request.use((cfg) => { const t = useAuthStore(store).token; if (t) cfg.headers.Authorization = `Bearer ${t}`; return cfg; });
  api.interceptors.response.use(undefined, (err) => { if (err.response?.status === 401) router.push({ name: "login" }); return Promise.reject(err); });
});
export { api };
```

```ts
// src/boot/auth.ts — восстановление сессии до первого рендера
export default boot(async ({ router, store }) => {
  const auth = useAuthStore(store);
  await auth.restore();
  router.beforeEach((to) => { if (to.meta.requiresAuth && !auth.isAuthenticated) return { name: "login" }; });
});
```

Типичные boot-файлы: `axios`, `i18n`, `auth/keycloak`, `sentry`, `pinia-plugins`, `vue-query`, глобальные компоненты/директивы, `dayjs` локаль, аналитика.

Параметры контекста: `app`, `router`, `store` (Pinia), `ssrContext`, `urlPath`, `publicPath`, `redirect`. Асинхронность: boot-файл может быть `async` — приложение дождётся.

Ограничение режима: `boot: [{ path: "sentry", server: false }]` — запускать только на клиенте (SSR).

## Нюансы и подводные камни

- Порядок boot-файлов важен (сначала Pinia/i18n, затем зависящие от них).
- Долгие асинхронные операции задерживают первый рендер.
- Boot выполняется один раз при старте (не при навигации).
- В SSR не обращайтесь к `window` в boot без защиты.

## Практика

1. Создайте boot для Axios с токеном и обработкой 401.
2. Добавьте boot для Sentry только на клиенте.
3. Восстановите сессию до инициализации роутера.

## Вопросы с ответами

> [!question]- Что такое boot-файл в Quasar?
> Модуль инициализации, выполняющийся до старта приложения и получающий доступ к `app`, `router` и `store`.

> [!question]- Когда не нужен boot?
> Если инициализацию можно сделать в `main`/composable без глобального доступа; boot нужен для регистрации плагинов и глобальных настроек.

## Связанные темы

- [[N:3ea3310486798162a794f205b40af87d]]
- [[N:3ea33104867981e3a864d2ad5c1b7f36]]
