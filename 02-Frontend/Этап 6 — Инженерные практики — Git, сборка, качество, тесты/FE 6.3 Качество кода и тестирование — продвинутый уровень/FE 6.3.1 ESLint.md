---
type: topic
domain: frontend
stage: 6
section: "6.3"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981488c3dddb07013e732
tags: [domain/frontend, stage/6, level/middle, topic/eslint, topic/lint, topic/quality, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# ESLint

↑ [[FE 6.3 Качество кода и тестирование — продвинутый уровень|6.3 Качество кода и тестирование: продвинутый уровень]] · → [[FE 6.3.2 Prettier|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Линтер — базовая гигиена команды. Спрашивают, чем ESLint отличается от Prettier, как настроить flat config и какие правила реально ловят баги.

## Суть

ESLint статически анализирует код и находит **потенциальные ошибки** (неиспользуемые переменные, забытый `await`, зависимости хуков) и **нарушения соглашений**. Форматирование — зона Prettier, не ESLint.

## Flat config (ESLint 9+)

```js
// eslint.config.js
import js from '@eslint/js'
import ts from 'typescript-eslint'
import vue from 'eslint-plugin-vue'

export default ts.config(
  js.configs.recommended,
  ...ts.configs.recommended,
  ...vue.configs['flat/recommended'],
  {
    files: ['**/*.{ts,vue}'],
    rules: {
      '@typescript-eslint/no-floating-promises': 'error',
      '@typescript-eslint/consistent-type-imports': 'warn',
      'no-console': ['warn', { allow: ['warn', 'error'] }],
    },
  },
  { ignores: ['dist', 'coverage'] },
)
```

Конфиг — обычный массив объектов, применяется сверху вниз; позднее правило переопределяет раннее. Старый `.eslintrc` с `extends` и `overrides` заменён на плоский формат.

## Что реально ловит баги

| Правило | От чего защищает |
|---|---|
| `no-floating-promises` | забытый `await`, необработанный reject |
| `no-unused-vars` | мёртвый код, опечатки |
| `eqeqeq` | неявное приведение типов |
| `vue/no-mutating-props` | мутация props в дочернем компоненте |
| `vue/require-v-for-key` | ошибки рендера списков |
| `import/no-cycle` | циклические зависимости |

## Type-aware правила

Правила `@typescript-eslint` с информацией о типах используют TypeScript-программу (`parserOptions.projectService: true`). Они мощнее, но медленнее: в CI запускайте полностью, в редакторе — по умолчанию.

## Практика

- уровни: `error` блокирует CI, `warn` — только подсказка; долго живущие warn превращаются в шум;
- `eslint --max-warnings 0` в CI;
- `--cache` ускоряет повторные прогоны;
- `eslint-disable` — только с комментарием-причиной.

## Вопросы с ответами

> [!question]- Чем ESLint отличается от Prettier?
> ESLint ищет ошибки и нарушения соглашений, Prettier только форматирует. Конфликтующие стилистические правила ESLint отключают через `eslint-config-prettier`.

> [!question]- Что такое flat config?
> Новый формат конфигурации ESLint: массив объектов с `files`, `rules`, `plugins`. Заменяет каскад `.eslintrc`, проще для понимания и композиции.

> [!question]- Как внедрить линтер в старый проект с тысячей ошибок?
> Включать по одному правилу на уровне warn, чинить автофиксом, потом переводить в error. Либо запускать линтер только на изменённых файлах (lint-staged), чтобы новый код был чистым.
