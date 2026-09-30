---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 20
status: todo
level: middle
notion_id: 3ea33104867981fcb497fa1eaf2daa2e
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/lazy-loading, topic/performance, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Асинхронные компоненты и lazy loading

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.19 Встроенные компоненты — Transition, KeepAlive, Teleport, Suspense|Предыдущая]] · → [[FE 4.1.21 Composables|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

















> [!info] Зачем это на собесе
> Как уменьшить начальный бандл: код-сплиттинг компонентов и маршрутов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
import { defineAsyncComponent } from "vue";

const HeavyChart = defineAsyncComponent(() => import("./HeavyChart.vue"));

const AsyncModal = defineAsyncComponent({
  loader: () => import("./Modal.vue"),
  loadingComponent: Spinner,
  errorComponent: ErrorBlock,
  delay: 200,            // не показывать loading сразу
  timeout: 10_000,
  hydrate: hydrateOnVisible(),      // 3.5: ленивая гидратация (SSR)
});
```

```ts
// Маршруты: динамический import — отдельный чанк на страницу
const routes = [{ path: "/reports", component: () => import("@/pages/ReportsPage.vue") }];
```

Стратегии:

| Что | Как |
|---|---|
| Маршруты | `() => import(...)` (по умолчанию для всех страниц) |
| Тяжёлые компоненты | `defineAsyncComponent` (графики, редакторы, PDF) |
| Показ по условию | `v-if` + async-компонент — грузится при первом показе |
| Предзагрузка | `import()` на hover/idle, `<link rel="prefetch">` (`/* webpackPrefetch: true */`, Vite: `modulepreload`) |
| Тяжёлые библиотеки | динамический `import("lib")` внутри обработчика |
| Ленивая гидратация | `hydrateOnVisible`, `hydrateOnIdle` (SSR) |

Vite создаёт отдельные чанки по динамическим импортам; `manualChunks` группирует библиотеки (vendor).

Индикация загрузки: `Suspense` или `loadingComponent`, скелетоны; обработка ошибок загрузки чанка (обновление приложения: `vite:preloadError` → перезагрузка).

## Нюансы и подводные камни

- Слишком мелкие чанки увеличивают число запросов; слишком крупные — задержку.
- После деплоя старые чанки исчезают: пользователи со старой вкладкой получают ошибку загрузки — обработайте.
- Асинхронные компоненты внутри `KeepAlive`/`Suspense` требуют аккуратности.
- Проверяйте состав бандла (`rollup-plugin-visualizer`).

## Практика

1. Сделайте маршруты ленивыми и посмотрите чанки в build.
2. Загрузите график только при открытии вкладки.
3. Настройте предзагрузку следующей страницы при наведении.

## Вопросы с ответами

> [!question]- Как уменьшить начальный бандл?
> Ленивые маршруты и тяжёлые компоненты (`import()`), разделение vendor-чанков, удаление неиспользуемого кода.

> [!question]- Что делать при ошибке загрузки чанка после деплоя?
> Обработать `vite:preloadError`/ошибку импорта и предложить перезагрузку.

## Связанные темы

- [[N:3ea33104867981d5912bd2c38599765c]]
- [[N:3ea33104867981c78367f30abc89391d]]
