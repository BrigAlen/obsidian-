---
type: topic
domain: frontend
stage: 6
section: "6.2"
order: 7
status: todo
level: middle
notion_id: 3ea331048679818d8857d000567e48fe
tags: [domain/frontend, stage/6, level/middle, topic/build, topic/ui-kit, topic/library, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Общая библиотека компонентов и composables

↑ [[FE 6.2 Сборка и инфраструктура — Vite, monorepo, CI-CD|6.2 Сборка и инфраструктура: Vite, monorepo, CI/CD]] · ← [[FE 6.2.6 Monorepo — pnpm workspaces, Nx, Turborepo|Предыдущая]] · → [[FE 6.2.8 CI-CD для фронтенда|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Как вынести общий UI и логику для нескольких приложений и не создать зависимость-монстра.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Состав библиотеки:

| Слой | Что | Пример |
|---|---|---|
| Токены | цвета, отступы, типографика | `@acme/tokens` (CSS-переменные, SCSS) |
| UI-kit | базовые компоненты | `BaseButton`, `BaseInput`, `DataTable` (на Quasar/Headless UI) |
| Composables | общая логика | `useDebounce`, `usePagination`, `useAuth` |
| Утилиты и типы | форматирование, валидаторы | `@acme/utils`, `@acme/types` |
| API-клиент | сгенерированный из OpenAPI | `@acme/api-client` |
| Конфиги | ESLint, TS, Vite | `@acme/config` |

Сборка библиотеки (Vite library mode):

```ts
// vite.config.ts
export default defineConfig({
  plugins: [vue(), dts({ tsconfigPath: "./tsconfig.build.json" })],
  build: {
    lib: { entry: "src/index.ts", formats: ["es"], fileName: "index", cssFileName: "style" },
    rollupOptions: { external: ["vue", "quasar", "vue-router", "pinia"], output: { preserveModules: true, globals: { vue: "Vue" } } },   // зависимости — внешние
  },
});
```

```json
// package.json
{ "name": "@acme/ui", "version": "1.4.0", "type": "module",
  "exports": { ".": { "types": "./dist/index.d.ts", "import": "./dist/index.js" }, "./style.css": "./dist/style.css" },
  "peerDependencies": { "vue": "^3.4.0", "quasar": "^2.16.0" }, "sideEffects": ["**/*.css"], "files": ["dist"] }
```

Публикация: приватный реестр (GitLab/GitHub Packages, Verdaccio, Artifactory), **Changesets/semantic-release** (версии и changelog по Conventional Commits).

Практики:

- **Vue/Quasar — peerDependencies**, а не dependencies (иначе две копии).
- API компонентов стабильный и документированный (Storybook, см. [[N:c070b4691d4845169cbfada7c1277b39]]), версионирование по semver, deprecation-цикл.
- Tree-shakeable экспорты (`preserveModules`, `sideEffects`).
- Тесты компонентов и визуальные регрессии.
- Типы: `.d.ts` через `vite-plugin-dts`, `vue-tsc`.
- Разработка в monorepo (`workspace:*`) или через локальную связь (`pnpm link`).
- Не переносите в библиотеку то, что используется одним приложением.

## Нюансы и подводные камни

- Дубликаты Vue/Pinia из-за неверных зависимостей → «inject() can only be used inside setup».
- Ломающие изменения без major-версии сломают все приложения.
- Глобальные стили библиотеки конфликтуют с приложением — изолируйте (префиксы, `@layer`).
- Слишком большая универсальность усложняет компоненты («API из 40 props»).
- Обновление всех потребителей: coordinated-релизы, codemods.

## Практика

1. Вынесите `BaseInput`, `BaseButton` и токены в пакет, соберите в library mode.
2. Настройте peerDependencies и проверьте отсутствие дубликатов Vue.
3. Автоматизируйте релизы через Changesets.

## Вопросы с ответами

> [!question]- Почему Vue в peerDependencies?
> Чтобы приложение и библиотека использовали один экземпляр Vue, иначе ломаются провайдеры и реактивность.

> [!question]- Как версионировать UI-библиотеку?
> По semver: ломающие изменения — major с миграционным гайдом, автоматизация через Changesets/semantic-release.

## Связанные темы

- [[N:3ea33104867981bb957ece3a6db635e6]]
- [[N:3ea33104867981149d11e5185d139a9b]]
