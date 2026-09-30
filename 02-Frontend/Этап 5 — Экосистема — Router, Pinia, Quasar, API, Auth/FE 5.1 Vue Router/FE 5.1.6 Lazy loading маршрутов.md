---
type: topic
domain: frontend
stage: 5
section: "5.1"
order: 6
status: todo
level: middle
notion_id: 3ea331048679813ebd28c2768696b2fc
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/router, topic/performance, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Lazy loading маршрутов

↑ [[FE 5.1 Vue Router|5.1 Vue Router]] · ← [[FE 5.1.5 Meta-поля маршрутов и доступ по ролям|Предыдущая]] · → [[FE 5.1.7 Scroll behavior|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Как уменьшить начальный бандл и что происходит при ошибке загрузки чанка.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Динамический `import()` создаёт отдельный чанк для страницы, загружаемый при первом переходе.

```ts
const routes = [
  { path: "/", component: HomePage },                                           // критичные — сразу
  { path: "/reports", component: () => import("@/pages/ReportsPage.vue") },     // ленивый чанк
  { path: "/admin", component: () => import(/* webpackChunkName: "admin" */ "@/pages/AdminPage.vue") },
];
```

Vite (Rollup) сам делит код; управление:

```ts
// vite.config.ts
build: { rollupOptions: { output: { manualChunks: { vendor: ["vue", "vue-router", "pinia"], charts: ["echarts"] } } } }
```

Оптимизации:

| Приём | Эффект |
|---|---|
| Ленивые страницы | меньше начальный JS |
| Предзагрузка (`prefetch`/`modulepreload`) | быстрее следующий переход |
| Предзагрузка по hover/видимости `RouterLink` | загрузка до клика |
| Группировка чанков | меньше запросов |
| Анализ бандла | `rollup-plugin-visualizer` |

Ошибка загрузки чанка после деплоя (старый чанк удалён):

```ts
router.onError((err, to) => {
  if (/Failed to fetch dynamically imported module|Importing a module script failed/.test(err.message)) location.assign(to.fullPath);  // жёсткая перезагрузка
});
window.addEventListener("vite:preloadError", () => location.reload());
```

Индикатор загрузки: глобальный прогресс-бар в `beforeEach/afterEach`, `Suspense`, скелетоны.

## Нюансы и подводные камни

- Слишком мелкие чанки → много запросов; слишком крупные → замедление.
- Не оборачивайте `defineAsyncComponent` вокруг роут-компонентов: роутер уже поддерживает ленивую загрузку.
- Кэширование чанков: имена с хэшем содержимого; `index.html` не кэшируйте долго.
- Загрузка на медленной сети: предзагрузка критичных страниц.

## Практика

1. Сделайте все страницы ленивыми и посмотрите чанки в `dist`.
2. Добавьте прогресс-бар при навигации.
3. Обработайте ошибку загрузки чанка перезагрузкой.

## Вопросы с ответами

> [!question]- Как реализовать lazy loading маршрутов?
> `component: () => import("./Page.vue")` — отдельный чанк подгружается при первом переходе.

> [!question]- Что делать, если после деплоя чанк не найден?
> Перехватить ошибку динамического импорта и перезагрузить страницу.

## Связанные темы

- [[N:3ea331048679819fbff4e2f18f924db2]]
- [[N:3ea3310486798159bab5eadb755f6602]]
