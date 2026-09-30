---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 23
status: todo
level: middle
notion_id: 3ea33104867981c1ae13c70ac05504c1
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/plugins, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Плагины Vue

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.22 VueUse|Предыдущая]] · → [[FE 4.1.24 Обработка ошибок — errorCaptured, app.config.errorHandler|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->























> [!info] Зачем это на собесе
> Как расширяют приложение: `app.use`, `provide`, глобальные компоненты и свойства.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Плагин — объект с методом `install(app, options)` или функция.

```ts
// plugins/toast.ts
import type { App, InjectionKey } from "vue";
export interface ToastApi { show(msg: string, type?: "info" | "error"): void }
export const ToastKey: InjectionKey<ToastApi> = Symbol("toast");

export default {
  install(app: App, options: { duration?: number } = {}) {
    const api: ToastApi = { show: (msg, type = "info") => console.log(type, msg) };
    app.provide(ToastKey, api);                           // предпочтительно: provide + composable useToast()
    app.component("ToastHost", ToastHost);                // глобальный компонент
    app.directive("focus", { mounted: (el) => el.focus() });
    app.config.globalProperties.$toast = api;             // Options API (устаревающий способ)
    app.config.errorHandler = (err) => api.show(String(err), "error");
  },
};

// main.ts
createApp(App).use(router).use(pinia).use(toast, { duration: 3000 }).mount("#app");
export const useToast = () => inject(ToastKey)!;
```

Что делают плагины: регистрируют компоненты/директивы, добавляют глобальные свойства, `provide` сервисы, внедряют собственный код (роутинг, состояние, i18n). Примеры: `vue-router`, `pinia`, `vue-i18n`, `Quasar`, `VueQuery`.

Типизация глобальных свойств:

```ts
declare module "vue" { interface ComponentCustomProperties { $toast: ToastApi } }
```

Рекомендации:

- Предпочитайте `provide/inject` + composable вместо `globalProperties`.
- Плагин должен быть идемпотентным и настраиваемым.
- Не добавляйте много глобального: это скрывает зависимости и мешает tree-shaking.

Порядок `app.use` важен, если плагины зависят друг от друга.

## Нюансы и подводные камни

- Глобальные компоненты попадают в бандл целиком (нет tree-shaking) — регистрируйте локально или через автоимпорт.
- Плагин с побочными эффектами в `install` выполняется при создании приложения (важно для тестов и SSR).
- `globalProperties` не доступны в `<script setup>` без `getCurrentInstance` — используйте `inject`.
- Несколько экземпляров приложения имеют отдельные плагины.

## Практика

1. Напишите плагин-тосты с `provide` и composable.
2. Добавьте глобальный обработчик ошибок в плагине.
3. Типизируйте `globalProperties`.

## Вопросы с ответами

> [!question]- Что такое плагин Vue?
> Объект/функция с `install(app, options)`, расширяющая приложение глобальными возможностями.

> [!question]- Как лучше делиться сервисом из плагина?
> Через `app.provide` и composable `useX()`, а не через `globalProperties`.

## Связанные темы

- [[N:3ea33104867981b2a2b2e2ba946e571c]]
- [[N:3ea3310486798126a148ed51c5b0b006]]
