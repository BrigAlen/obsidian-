---
type: topic
domain: frontend
stage: 7
section: "7.2"
order: 5
status: todo
level: senior
notion_id: 3ea3310486798121992ad926900a9e48
tags: [domain/frontend, stage/7, level/senior, topic/tree-shaking, topic/bundle, topic/esm, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Tree shaking и размер бандла

↑ [[FE 7.2 Рендеринг и производительность|7.2 Рендеринг и производительность]] · ← [[FE 7.2.4 Code splitting и lazy loading|Предыдущая]] · → [[FE 7.2.6 Оптимизация изображений и шрифтов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Объясняет, почему import из lodash раздувает бандл и как этого избежать.

## Что такое tree shaking

Удаление неиспользуемого кода при сборке. Работает со статическими ES-модулями (`import`/`export`), потому что их структура известна на этапе сборки. CommonJS (`require`) плохо поддаётся.

## Условия

- библиотека в ESM;
- `"sideEffects": false` в `package.json` библиотеки (или список файлов с побочными эффектами);
- импорт именованных экспортов, а не всего объекта;
- нет побочных эффектов на верхнем уровне модуля.

```ts
import _ from 'lodash'                 // весь lodash
import { debounce } from 'lodash-es'   // только debounce
import debounce from 'lodash/debounce' // тоже только он
```

## Анализ бандла

`rollup-plugin-visualizer` или `vite-bundle-visualizer`, `source-map-explorer`, `webpack-bundle-analyzer`. Ищем дубликаты пакетов и тяжёлые зависимости.

## Как уменьшить

| Проблема | Решение |
|---|---|
| moment.js (с локалями) | dayjs или date-fns |
| Полная иконочная библиотека | импорт отдельных иконок |
| Полифиллы для всех | browserslist и `targets`, полифиллы по необходимости |
| Дубли пакетов | `npm dedupe`, алиасы |
| Большие библиотеки | лёгкие аналоги, динамический импорт |

Сжатие: gzip и Brotli на сервере или CDN. Минификация: esbuild или terser.

## Вопросы с ответами

> [!question]- Почему tree shaking не работает с CommonJS?
> `require` динамичен, что импортируется, определяется во время выполнения. Для ESM зависимости статически известны.

> [!question]- Что значит sideEffects: false?
> Пакет сообщает сборщику, что неиспользуемые импорты можно безопасно удалять, так как модули не выполняют побочных действий при импорте.
