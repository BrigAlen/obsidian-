---
type: topic
domain: frontend
stage: 7
section: "7.2"
order: 4
status: todo
level: senior
notion_id: 3ea33104867981b78493d6ab19a8804b
tags: [domain/frontend, stage/7, level/senior, topic/code-splitting, topic/lazy, topic/vite, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Code splitting и lazy loading

↑ [[FE 7.2 Рендеринг и производительность|7.2 Рендеринг и производительность]] · ← [[FE 7.2.3 Core Web Vitals — LCP, INP, CLS|Предыдущая]] · → [[FE 7.2.5 Tree shaking и размер бандла|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->











> [!info] Зачем это на собесе
> Уменьшение начального JS — главный рычаг быстрой загрузки SPA.

## Идея

Не отдавать весь код сразу: разбить на чанки и подгружать по необходимости.

## Способы

```ts
// маршруты
const routes = [
  { path: '/reports', component: () => import('./pages/ReportsPage.vue') },
]

// компоненты
const Editor = defineAsyncComponent({
  loader: () => import('./Editor.vue'),
  loadingComponent: Spinner,
  delay: 200,
})

// библиотеки по требованию
async function exportXlsx() {
  const { utils, writeFile } = await import('xlsx')
}
```

## Vite / Rollup

```ts
build: {
  rollupOptions: {
    output: {
      manualChunks: { vendor: ['vue', 'vue-router', 'pinia'] },
    },
  },
}
```

## Стратегии предзагрузки

- `<link rel="prefetch">` — на простое время браузера;
- `import(/* webpackPrefetch: true */ ...)` (Webpack), в Vite — автоматический `modulepreload`;
- prefetch по hover ссылки или при появлении в viewport (`IntersectionObserver`).

## Нюансы

- слишком много мелких чанков дают лишние запросы (HTTP/2 смягчает);
- общие зависимости выносятся в shared chunk автоматически;
- показывать skeleton, обрабатывать ошибку загрузки чанка (сеть, устаревший деплой);
- разделять по маршрутам в первую очередь.

## Вопросы с ответами

> [!question]- С чего начать уменьшение бандла?
> Разделить по маршрутам, вынести тяжёлые библиотеки (графики, редакторы) в динамический импорт, проверить визуализатором состав бандла.

> [!question]- Что делать при ошибке загрузки чанка после деплоя?
> Ловить ошибку динамического импорта и перезагружать страницу, хранить старые ассеты на CDN.
