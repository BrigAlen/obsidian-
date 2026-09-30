---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 17
status: todo
level: middle
notion_id: 3ea331048679813da123f4a332bbf8c1
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/testing, topic/ci, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Тестирование типов: expectTypeOf, vue-tsc в CI

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.16 tsconfig и strict-режим|Предыдущая]] · → [[FE 3.1.18 Задачи на TypeScript|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Как гарантировать корректность типов, особенно в библиотеках и API-слое.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Способы проверить типы:

| Способ | Что проверяет |
|---|---|
| `tsc --noEmit` / `vue-tsc --noEmit` | корректность типов всего проекта (в CI обязательно) |
| `expectTypeOf` (Vitest) | точный тип значения/функции |
| `tsd`, `dtslint` | типы библиотек |
| `// @ts-expect-error` | код **должен** вызывать ошибку типа |
| Линтеры (`typescript-eslint`) | типозависимые правила: `no-floating-promises`, `no-unsafe-*` |

```ts
import { expectTypeOf, describe, it } from "vitest";

describe("типы утилит", () => {
  it("pick возвращает подмножество", () => {
    expectTypeOf(pick({ a: 1, b: "x" }, ["a"])).toEqualTypeOf<{ a: number }>();
    expectTypeOf<ApiResponse<User>["data"]>().toEqualTypeOf<User>();
    expectTypeOf(fn).parameter(0).toBeString();
    expectTypeOf(fn).returns.toMatchTypeOf<Promise<unknown>>();
  });

  it("отвергает неверные аргументы", () => {
    // @ts-expect-error — id должен быть числом
    getUser("1");
  });
});
```

Vitest: `vitest --typecheck` запускает файлы `*.test-d.ts`.

```yaml
# CI
- run: npm ci
- run: npx vue-tsc --noEmit
- run: npx eslint . --max-warnings 0
- run: npx vitest run --typecheck
```

Дополнительно: проверка сгенерированных API-типов (`openapi-typescript`) после изменения схемы; `knip`/`ts-prune` для неиспользуемых экспортов.

## Нюансы и подводные камни

- `toEqualTypeOf` строгий (идентичность), `toMatchTypeOf` — совместимость.
- `@ts-expect-error` при исчезновении ошибки сам становится ошибкой — это его польза.
- Не отключайте проверки в CI ради скорости.
- Типы в тестах не выполняются в рантайме — используйте вместе с обычными тестами.

## Практика

1. Добавьте `vue-tsc --noEmit` в pipeline.
2. Напишите type-тесты для 3 своих утилит.
3. Настройте `no-floating-promises`.

## Вопросы с ответами

> [!question]- Как проверить типы в CI?
> `tsc --noEmit` (для Vue — `vue-tsc --noEmit`) отдельным шагом.

> [!question]- Зачем `@ts-expect-error`?
> Утверждает, что строка должна вызывать ошибку типа, и сигнализирует, если ошибки нет.

## Связанные темы

- [[N:3ea33104867981928f36f6c0348e7e23]]
- [[N:3ea331048679819c9b56f7afc4868cd5]]
