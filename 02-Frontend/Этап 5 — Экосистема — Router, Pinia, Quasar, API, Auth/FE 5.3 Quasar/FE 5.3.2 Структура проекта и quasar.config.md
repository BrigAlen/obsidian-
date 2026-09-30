---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 2
status: todo
level: middle
notion_id: 3ea3310486798162a794f205b40af87d
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/config, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Структура проекта и quasar.config

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.1 Что такое Quasar, CLI и Vite-режим|Предыдущая]] · → [[FE 5.3.3 Boot files|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Как организован проект Quasar и что настраивается в `quasar.config`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```text
src/
  assets/            статические ресурсы (обрабатываются сборкой)
  boot/              boot-файлы (инициализация приложения)
  components/        общие компоненты
  css/               app.scss, quasar.variables.scss
  layouts/           MainLayout.vue, AuthLayout.vue
  pages/             страницы (маршруты)
  router/            index.ts, routes.ts
  stores/            Pinia
  i18n/              переводы
public/              статика без обработки (favicon)
quasar.config.ts     основной конфиг
src-pwa/, src-electron/, src-capacitor/, src-ssr/   режимы
```

```ts
// quasar.config.ts
export default defineConfig((ctx) => ({
  boot: ["i18n", "axios", "auth"],
  css: ["app.scss"],
  extras: ["roboto-font", "material-icons"],
  build: {
    target: { browser: ["es2022", "chrome110"] },
    vueRouterMode: "history",                    // hash | history
    publicPath: "/",
    env: { API_URL: process.env.API_URL },       // process.env.* и import.meta.env
    extendViteConf(cfg) { /* доп. настройки Vite */ },
    vitePlugins: [["vite-plugin-checker", { vueTsc: true }]],
  },
  devServer: { port: 9000, proxy: { "/api": { target: "http://localhost:5000", changeOrigin: true } } },
  framework: {
    config: { dark: "auto", brand: { primary: "#1976d2" } },
    plugins: ["Notify", "Dialog", "Loading", "LocalStorage"],
    iconSet: "material-icons", lang: "ru",
  },
  animations: [],
  ssr: {}, pwa: { workboxMode: "GenerateSW" },
}));
```

Основные секции: `boot`, `css`, `extras`, `build`, `devServer`, `framework` (плагины, конфиг, язык), `animations`, `sourceFiles`, `htmlVariables`, настройки режимов.

Переменные окружения: `.env`, `.env.production`; передача через `build.env`; `import.meta.env` в коде.

Маршруты и страницы: `routes.ts` подключает layout и страницы (`component: () => import(...)`).

## Нюансы и подводные камни

- Изменения `quasar.config` требуют перезапуска dev-сервера.
- Не храните секреты в `build.env`: они попадают в бандл.
- Плагины Quasar нужно перечислить в `framework.plugins`, иначе они недоступны.
- `vueRouterMode: "history"` требует fallback на сервере.
- Прокси `devServer` действует только в разработке.

## Практика

1. Настройте прокси `/api` и переменные окружения.
2. Добавьте плагины Notify и Dialog в конфиг.
3. Подключите проверку типов при сборке.

## Вопросы с ответами

> [!question]- Где подключаются плагины Quasar?
> В `framework.plugins` файла `quasar.config`.

> [!question]- Чем `public` отличается от `src/assets`?
> `public` копируется как есть, `assets` обрабатываются сборщиком (хэши имён, оптимизация).

## Связанные темы

- [[N:3ea33104867981319af3fe3805ab8528]]
- [[N:3ea33104867981d89554c287a6494d1c]]
