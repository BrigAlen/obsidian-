---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 16
status: todo
level: middle
notion_id: 3ea33104867981928f36f6c0348e7e23
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/tsconfig, topic/strict, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# tsconfig и strict-режим

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.15 Декларации и .d.ts|Предыдущая]] · → [[FE 3.1.17 Тестирование типов — expectTypeOf, vue-tsc в CI|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Ждут знания ключевых флагов строгости и отличия компиляции от проверки типов в Vite.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["ES2023", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitOverride": true,
    "noFallthroughCasesInSwitch": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true,
    "noEmit": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] },
    "types": ["vite/client"]
  },
  "include": ["src/**/*.ts", "src/**/*.vue", "env.d.ts"]
}
```

`strict: true` включает группу:

| Флаг | Эффект |
|---|---|
| `noImplicitAny` | запрет неявного `any` |
| `strictNullChecks` | `null/undefined` — отдельные типы |
| `strictFunctionTypes` | контравариантность параметров |
| `strictBindCallApply` | проверка `bind/call/apply` |
| `strictPropertyInitialization` | поля класса инициализируются |
| `noImplicitThis`, `useUnknownInCatchVariables`, `alwaysStrict` | остальное |

Дополнительно: `noUncheckedIndexedAccess` (доступ по индексу может вернуть `undefined`), `exactOptionalPropertyTypes`, `noUnusedLocals/Parameters`.

Как это работает в проектах на Vite: **Vite/esbuild только стирают типы**, проверку выполняет `tsc --noEmit` или **`vue-tsc --noEmit`** (для `.vue`) отдельным шагом в CI. Для монорепо — `references` и `composite`, общий `tsconfig.base.json`.

Внедрение в legacy-код: включать флаги по одному, начиная с `noImplicitAny`; использовать `// @ts-expect-error` с пояснением (лучше, чем `@ts-ignore`).

## Нюансы и подводные камни

- `isolatedModules` требует, чтобы каждый файл можно было транспилировать отдельно (нет `const enum`, реэкспорт типов через `export type`).
- `paths` нужно дублировать в сборщике (`alias`).
- `skipLibCheck: true` ускоряет, но скрывает ошибки в `.d.ts`.
- Слишком мягкий `strict: false` лишает TS большей части пользы.

## Практика

1. Включите `strict` в существующем проекте и исправьте ошибки поэтапно.
2. Добавьте `vue-tsc --noEmit` в CI.
3. Настройте алиасы `@/*` в tsconfig и Vite.

## Вопросы с ответами

> [!question]- Что включает `strict`?
> Набор строгих проверок: `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes` и другие.

> [!question]- Проверяет ли Vite типы?
> Нет, он только удаляет типы; проверка — отдельно через `tsc`/`vue-tsc`.

## Связанные темы

- [[N:3ea331048679817b8eecc9de531cdcaa]]
- [[N:3ea331048679813da123f4a332bbf8c1]]
