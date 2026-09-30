---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 1
status: todo
level: middle
notion_id: 3ea3310486798159b0ccf7fe498691fa
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/types, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Базовые типы, any, unknown, never, void

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · → [[FE 3.1.2 Interface и type — различия|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






















> [!info] Зачем это на собесе
> Разница `any` и `unknown` и роль `never` — вопросы на понимание системы типов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

TypeScript — надстройка над JS со статической типизацией; типы **стираются** при компиляции.

```ts
const n: number = 1, s: string = "a", b: boolean = true;
const arr: number[] = [1], tuple: [string, number] = ["a", 1];
const id: bigint = 1n, sym: symbol = Symbol();
let u: undefined, nu: null;
let x = 5;                  // вывод типов: number
const lit = "a";            // тип литерал "a"
```

| Тип | Смысл |
|---|---|
| `any` | отключает проверку: небезопасный «обход» |
| `unknown` | безопасный «любой»: нужно сузить тип перед использованием |
| `never` | значений нет: функция не возвращает, недостижимая ветка, пустое пересечение |
| `void` | функция не возвращает значимого результата |
| `object`, `{}`, `Object` | нестрогие; предпочитайте конкретные структуры или `Record<string, unknown>` |
| `null`/`undefined` | отдельные типы при `strictNullChecks` |

```ts
function parse(json: string): unknown { return JSON.parse(json); }
const v = parse("1");
// v.toFixed()          // ошибка: сначала сузить
if (typeof v === "number") v.toFixed();

function fail(msg: string): never { throw new Error(msg); }
function exhaustive(x: never): never { throw new Error(`Unexpected: ${x}`); }   // проверка полноты switch

let a: any = "x"; a.foo.bar();     // компилируется, падает в рантайме
```

Утверждения типов: `value as string`, `<string>value`, non-null `x!` — обещания компилятору, не проверки.

## Нюансы и подводные камни

- `any` «заражает» код: результат операций с `any` тоже `any`. Включите `noImplicitAny`, используйте `unknown`.
- `as` не преобразует значение: ложное утверждение ведёт к ошибке в рантайме.
- Массивы: `T[]` и `Array<T>` равнозначны; `readonly T[]` для неизменяемых.
- `void` не то же, что `undefined` (для типов коллбэков).
- `Object.keys` возвращает `string[]`, а не `(keyof T)[]`.

## Практика

1. Замените `any` на `unknown` в утилите парсинга и добавьте сужение.
2. Сделайте проверку полноты `switch` через `never`.
3. Включите `noImplicitAny` и исправьте ошибки.

## Вопросы с ответами

> [!question]- Чем `unknown` отличается от `any`?
> `any` отключает проверки, `unknown` требует сужения типа перед использованием.

> [!question]- Что такое `never`?
> Тип значений, которых не существует: результат недостижимого кода, функции без возврата, пустого пересечения.

## Связанные темы

- [[N:3ea33104867981978640c558af5eaf71]]
- [[N:3ea33104867981348550f303d11f5b03]]
