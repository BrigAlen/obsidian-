---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 15
status: todo
level: middle
notion_id: 3ea331048679817b8eecc9de531cdcaa
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/declarations, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Декларации и .d.ts

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.14 Декораторы|Предыдущая]] · → [[FE 3.1.16 tsconfig и strict-режим|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Как типизировать JS-библиотеки и глобальные объекты.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Файлы `.d.ts` содержат только типы (без кода) и описывают форму существующего JS.

```ts
// global.d.ts — расширение глобальных типов
declare global {
  interface Window { __APP_CONFIG__: { apiUrl: string } }
}
export {};                                              // делает файл модулем

// env.d.ts (Vite)
/// <reference types="vite/client" />
interface ImportMetaEnv { readonly VITE_API_URL: string }
interface ImportMeta { readonly env: ImportMetaEnv }

// Модули без типов
declare module "legacy-lib" { export function run(x: string): void; }
declare module "*.svg" { const src: string; export default src; }
declare module "*.vue" { import type { DefineComponent } from "vue"; const c: DefineComponent<{}, {}, any>; export default c; }

// Дополнение типов библиотеки (module augmentation)
declare module "vue-router" { interface RouteMeta { requiresAuth?: boolean; roles?: string[] } }
declare module "pinia" { export interface PiniaCustomProperties { $api: ApiClient } }
```

| Источник типов | Описание |
|---|---|
| Пакет с `types`/`typings` в `package.json` | типы поставляются автором |
| `@types/*` (DefinitelyTyped) | сообщество |
| Собственные `.d.ts` | для нетипизированного кода |
| Генерация (`tsc --declaration`) | для собственных библиотек |
| `skipLibCheck` | не проверять `.d.ts` в `node_modules` (ускоряет) |

Ключевые слова: `declare` (объявление без реализации), `/// <reference>`, `export as namespace` (UMD), `typeRoots`, `types`.

## Нюансы и подводные камни

- Файл без `import/export` — глобальный скрипт: объявления попадают в глобальную область.
- `declare module "x"` без тела делает модуль `any` — отключает типизацию.
- Расширение типов библиотеки требует точного совпадения имени модуля и файла, включённого в `tsconfig`.
- Неверные `@types` версии вызывают конфликты.

## Практика

1. Типизируйте `import.meta.env` и глобальный `window.__APP_CONFIG__`.
2. Расширьте `RouteMeta` в vue-router.
3. Напишите `.d.ts` для небольшой нетипизированной библиотеки.

## Вопросы с ответами

> [!question]- Что такое `.d.ts`?
> Файл деклараций типов без реализации, описывающий структуру JS-кода.

> [!question]- Как добавить поле к типу из библиотеки?
> Через module augmentation: `declare module "lib" { interface X { ... } }`.

## Связанные темы

- [[N:3ea331048679814d8d16e9408e1b696e]]
- [[N:3ea33104867981928f36f6c0348e7e23]]
