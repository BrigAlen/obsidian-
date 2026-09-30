---
type: topic
domain: frontend
stage: 6
section: "6.2"
order: 3
status: todo
level: middle
notion_id: 3ea331048679819ebc53c4173bc9fc78
tags: [domain/frontend, stage/6, level/middle, topic/build, topic/webpack, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Webpack: основы и отличия от Vite

↑ [[FE 6.2 Сборка и инфраструктура — Vite, monorepo, CI-CD|6.2 Сборка и инфраструктура: Vite, monorepo, CI/CD]] · ← [[FE 6.2.2 Vite — dev server, esbuild, Rollup, HMR|Предыдущая]] · → [[FE 6.2.4 Переменные окружения и режимы сборки|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->











> [!info] Зачем это на собесе
> Легаси-проекты на webpack встречаются; нужно знать ключевые понятия и отличия.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Ключевые понятия webpack:

| Понятие | Смысл |
|---|---|
| `entry` | точка входа графа |
| `output` | куда и как писать результат (`filename: "[name].[contenthash].js"`) |
| `loaders` | преобразуют файлы (`babel-loader`, `ts-loader`, `vue-loader`, `css-loader`, `sass-loader`, `asset modules`) |
| `plugins` | расширяют сборку (`HtmlWebpackPlugin`, `MiniCssExtractPlugin`, `DefinePlugin`, `CopyPlugin`, `BundleAnalyzerPlugin`) |
| `mode` | `development`/`production` (оптимизации) |
| `optimization` | `splitChunks`, `runtimeChunk`, `minimizer`, `usedExports` |
| `resolve` | алиасы, расширения |
| `devServer` | HMR, прокси |
| Module Federation | микрофронтенды (шаринг модулей между сборками) |

```js
module.exports = {
  entry: "./src/main.ts",
  output: { path: path.resolve("dist"), filename: "[name].[contenthash:8].js", clean: true },
  module: { rules: [{ test: /\.vue$/, loader: "vue-loader" }, { test: /\.ts$/, loader: "ts-loader", options: { appendTsSuffixTo: [/\.vue$/] } }, { test: /\.scss$/, use: ["style-loader", "css-loader", "sass-loader"] }] },
  plugins: [new VueLoaderPlugin(), new HtmlWebpackPlugin({ template: "public/index.html" })],
  optimization: { splitChunks: { chunks: "all" } },
  devServer: { hot: true, historyApiFallback: true },
};
```

| Критерий | webpack | Vite |
|---|---|---|
| Dev-старт | собирает весь бандл (медленнее на больших проектах) | нативные ESM, мгновенный старт |
| HMR | быстро, но зависит от размера проекта | стабильно быстро |
| Конфигурация | мощная, но сложная и многословная | проще, разумные значения по умолчанию |
| Экосистема | огромная, зрелая (loaders/plugins) | быстро растёт, совместима с Rollup-плагинами |
| Prod-сборка | webpack | Rollup/Rolldown |
| Module Federation | нативно | плагин (`@originjs/vite-plugin-federation`, native federation) |
| Легаси, кастомные пайплайны | лучше | хуже |

Миграция на Vite: заменить `vue-cli` → `vite`, `require` → `import`, `process.env.X` → `import.meta.env.VITE_X`, алиасы, обработка ассетов (`require("./img.png")` → `import`/`new URL`), проверка плагинов; либо **Rspack** — практически drop-in замена webpack на Rust.

## Нюансы и подводные камни

- Конфигурация webpack легко раздувается: используйте `webpack-merge` для окружений.
- Разные версии loaders/plugins конфликтуют.
- Медленный dev на больших проектах: кэш (`cache: { type: "filesystem" }`), thread-loader, замена Babel на SWC/esbuild.
- CommonJS-специфика (`require`, `module.exports`) при миграции.
- Vue CLI в режиме поддержки — рекомендуется миграция на Vite.

## Практика

1. Прочитайте конфиг существующего webpack-проекта и опишите entry/loaders/plugins.
2. Проанализируйте бандл через `webpack-bundle-analyzer`.
3. Составьте план миграции на Vite.

## Вопросы с ответами

> [!question]- Чем loader отличается от plugin?
> Loader преобразует отдельные файлы при импорте, plugin вмешивается в жизненный цикл сборки в целом.

> [!question]- Основное отличие webpack и Vite?
> Webpack собирает бандл на dev-старте, Vite отдаёт нативные ES-модули и собирает только для продакшена.

## Связанные темы

- [[N:3ea33104867981f796abf81be5c4e890]]
- [[N:3ea33104867981ae9b4bf9d29143eb13]]
