---
type: topic
domain: frontend
stage: 1
section: "1.4"
order: 13
status: todo
level: junior
notion_id: 3ea33104867981daa8b5d128045f2f66
tags: [domain/frontend, stage/1, level/junior, topic/javascript, topic/modules, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Модули: ESM и CommonJS

↑ [[FE 1.4 JavaScript — основы|1.4 JavaScript: основы]] · ← [[FE 1.4.12 Обработка ошибок|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Различия форматов модулей и «живых» привязок; важно для сборки и Node.js.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| | ESM (ES Modules) | CommonJS |
|---|---|---|
| Синтаксис | `import/export` | `require/module.exports` |
| Загрузка | статический анализ, асинхронная | динамическая, синхронная |
| Привязки | «живые» (live bindings) | копия значения на момент require |
| Tree shaking | возможен | затруднён |
| Строгий режим | всегда | нет |
| Top-level await | да | нет |
| `this` на верхнем уровне | `undefined` | `module.exports` |
| Браузер | нативно (`type="module"`) | нет (нужна сборка) |

```js
// math.js
export const PI = 3.14;
export function sum(a, b) { return a + b; }
export default class Calc {}

// app.js
import Calc, { PI, sum as add } from "./math.js";
import * as math from "./math.js";
const { heavy } = await import("./heavy.js");     // динамический импорт → код-сплиттинг
export { add };            // реэкспорт: export { x } from "./x.js";
```

```js
// CommonJS
const fs = require("node:fs");
module.exports = { read };
```

Особенности ESM: импорты «поднимаются», выполняются один раз (кэш модулей), циклические зависимости разрешаются через живые привязки; пути с расширением (`./a.js`) в браузере и Node.

Сборщики (Vite, webpack, Rollup, esbuild) объединяют модули, выполняют tree shaking, code splitting. Пакеты: поля `type`, `exports`, `main`, `module` в `package.json`.

## Нюансы и подводные камни

- Смешение ESM и CJS: `require` ESM-модуля недоступно, нужен `import()`; `__dirname` отсутствует в ESM (`import.meta.url`).
- Побочные эффекты при импорте (код на верхнем уровне) выполняются один раз.
- Tree shaking требует чистых модулей и `sideEffects: false` в `package.json`.
- Именованные и default-экспорты: default затрудняет переименование и автодополнение.
- Циклические зависимости приводят к `undefined` или TDZ.

## Практика

1. Разделите скрипт на модули и подключите как `type="module"`.
2. Выделите тяжёлую часть в динамический `import()` и посмотрите чанк в Network.
3. Найдите циклическую зависимость через `madge`.

## Вопросы с ответами

> [!question]- Чем ESM отличается от CommonJS?
> ESM — статические импорты и живые привязки, асинхронная загрузка; CJS — динамический `require` и копия значений.

> [!question]- Что такое tree shaking?
> Удаление неиспользуемых экспортов при сборке; работает благодаря статической структуре ESM.

## Связанные темы

- [[N:3ea331048679816da10fe17794cbb365]]
- [[N:3ea33104867981789846e17e97e590c4]]
