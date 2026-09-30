---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 12
status: todo
level: middle
notion_id: 3ea33104867981b59058cb6474a9b446
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/template-literals, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Template literal types

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.11 Mapped и conditional types, infer|Предыдущая]] · → [[FE 3.1.13 Структурная типизация, вариантность, satisfies|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> Строгая типизация строк: маршруты, события, CSS-классы.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Шаблонные литеральные типы строят строковые типы из других.

```ts
type Method = "get" | "post";
type Endpoint = `/api/${"users" | "orders"}`;                  // "/api/users" | "/api/orders"
type Route = `${Uppercase<Method>} ${Endpoint}`;               // "GET /api/users" | ...

type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickHandler = EventName<"click">;                         // "onClick"

// Парсинг строк на уровне типов
type Params<P extends string> = P extends `${string}:${infer Name}/${infer Rest}` ? Name | Params<`/${Rest}`> : P extends `${string}:${infer Name}` ? Name : never;
type P = Params<"/users/:id/posts/:postId">;                    // "id" | "postId"

type Split<S extends string, D extends string> = S extends `${infer H}${D}${infer T}` ? [H, ...Split<T, D>] : [S];
type CSSUnit = `${number}${"px" | "rem" | "%"}`;                 // "10px" | "1.5rem" ...
```

Встроенные манипуляторы: `Uppercase`, `Lowercase`, `Capitalize`, `Uncapitalize`.

Применения:

- Типизация имён событий и обработчиков (`on${Capitalize<K>}`).
- Типобезопасные роутеры (`vue-router` с `typed-router`).
- Ключи i18n (`common.buttons.save`), вывод путей вложенных объектов.
- Классы утилит (`text-${Size}`).

Комбинация с mapped types и `as`: ключи с префиксом/суффиксом.

## Нюансы и подводные камни

- Комбинаторный взрыв union: `${A}${B}${C}` с большими union даёт тысячи вариантов.
- Ограничение глубины рекурсии.
- Сложные строковые парсеры в типах сложно поддерживать.
- Ошибки читаются трудно.

## Практика

1. Типизируйте события `onClick`, `onFocus` из списка имён.
2. Выведите параметры маршрута из строки-шаблона.
3. Сгенерируйте тип путей вложенного объекта переводов.

## Вопросы с ответами

> [!question]- Что такое template literal types?
> Типы, строящие строковые литералы из других типов по шаблону вида `` `prefix-${T}` ``.

> [!question]- Пример применения?
> Типизация имён событий и обработчиков, путей API и ключей i18n.

## Связанные темы

- [[N:3ea331048679816495f6eb1b9f2919b0]]
- [[N:3ea33104867981a1b567e0d670b97106]]
