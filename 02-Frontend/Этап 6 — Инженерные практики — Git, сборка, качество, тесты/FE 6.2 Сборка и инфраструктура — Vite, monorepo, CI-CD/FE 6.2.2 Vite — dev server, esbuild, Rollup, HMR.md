---
type: topic
domain: frontend
stage: 6
section: "6.2"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981f796abf81be5c4e890
tags: [domain/frontend, stage/6, level/middle, topic/build, topic/vite, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Vite: dev server, esbuild, Rollup, HMR

↑ [[FE 6.2 Сборка и инфраструктура — Vite, monorepo, CI-CD|6.2 Сборка и инфраструктура: Vite, monorepo, CI/CD]] · ← [[FE 6.2.1 Зачем нужны бандлеры|Предыдущая]] · → [[FE 6.2.3 Webpack — основы и отличия от Vite|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Почему Vite быстрый и как устроены dev и prod-режимы.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Dev-сервер**: не собирает весь бандл — отдаёт исходники как нативные ES-модули; браузер сам запрашивает импорты. Зависимости из `node_modules` предварительно собираются **esbuild** (pre-bundling: CJS → ESM, склейка множества внутренних модулей) и кэшируются. Трансформации — по запросу (TS, Vue SFC, JSX, CSS).

**HMR**: при изменении файла заменяется только затронутый модуль без перезагрузки страницы (для Vue — сохраняется состояние компонента).

**Prod-сборка**: **Rollup** (в новых версиях — Rolldown): tree shaking, code splitting, хэши, минификация (esbuild/Terser), CSS-извлечение.

```ts
// vite.config.ts
export default defineConfig(({ mode }) => ({
  plugins: [vue(), vueJsx(), Components(), AutoImport({ imports: ["vue", "vue-router"] }), visualizer({ gzipSize: true })],
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  server: { port: 5173, proxy: { "/api": { target: "http://localhost:5000", changeOrigin: true } } },
  build: {
    target: "es2020", sourcemap: true, chunkSizeWarningLimit: 600,
    rollupOptions: { output: { manualChunks: { vendor: ["vue", "vue-router", "pinia"] } } },
  },
  css: { preprocessorOptions: { scss: { additionalData: `@use "@/styles/vars" as *;` } } },
  define: { __APP_VERSION__: JSON.stringify(process.env.npm_package_version) },
  test: { environment: "jsdom" },                                     // Vitest использует тот же конфиг
}));
```

| Возможность | Описание |
|---|---|
| Плагины | совместимы с Rollup + хуки Vite (`configureServer`, `transformIndexHtml`) |
| Переменные окружения | `import.meta.env.VITE_*`, `.env.[mode]` |
| Ассеты | `?url`, `?raw`, `?worker`, `import.meta.glob`, `new URL(..., import.meta.url)` |
| Библиотечный режим | `build.lib` |
| SSR | `vite build --ssr` |
| Preview | `vite preview` (проверка prod-сборки) |
| Оптимизации | `optimizeDeps`, `manualChunks`, `modulePreload`, `build.cssCodeSplit` |
| Legacy | `@vitejs/plugin-legacy` |

Причины скорости: нативные ESM (нет бандлинга при старте), esbuild (Go, на порядки быстрее JS-сборщиков), ленивые трансформации, кэш.

## Нюансы и подводные камни

- Различие dev (ESM без бандла) и prod (Rollup) — редкие «работает в dev, ломается в prod»: проверяйте `preview`.
- Зависимости с CJS/неправильными экспортами требуют `optimizeDeps.include`.
- Переменные без префикса `VITE_` в клиент не попадают.
- Большое число модулей в dev даёт много запросов (влияет на тяжёлые проекты, помогает pre-bundling).
- Плагин порядок важен (`enforce: "pre" | "post"`).

## Практика

1. Настройте алиасы, прокси, `manualChunks` и визуализатор.
2. Напишите свой мини-плагин (`transform`).
3. Найдите расхождение dev и prod через `vite preview`.

## Вопросы с ответами

> [!question]- Почему Vite быстрее webpack в dev?
> Не собирает бандл: отдаёт нативные ES-модули по запросу, зависимости pre-bundle'ятся esbuild и кэшируются.

> [!question]- Чем собирает prod Vite?
> Rollup (Rolldown в новых версиях) с tree shaking и разделением кода.

## Связанные темы

- [[N:3ea33104867981bab2c4fa6bd251ed0d]]
- [[N:3ea331048679819ebc53c4173bc9fc78]]
