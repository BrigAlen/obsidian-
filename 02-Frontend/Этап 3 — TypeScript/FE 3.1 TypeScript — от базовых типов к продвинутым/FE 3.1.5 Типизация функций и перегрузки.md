---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 5
status: todo
level: middle
notion_id: 3ea331048679816a8d8fc767f7201f2e
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/functions, topic/overloads, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Типизация функций и перегрузки

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.4 Utility types|Предыдущая]] · → [[FE 3.1.6 Narrowing и type guards|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Как типизировать колбэки, необязательные параметры и функции с разной сигнатурой.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
function add(a: number, b = 0, ...rest: number[]): number { return a + b + rest.reduce((s, x) => s + x, 0); }
const fn: (x: string) => void = (x) => console.log(x);
type Predicate<T> = (item: T, index: number) => boolean;
type Callback = { (err: Error | null, data?: string): void; timeout?: number };   // callable с свойством
function greet(this: HTMLElement, name?: string) {}                                // типизация this
```

**Перегрузки** — несколько сигнатур для одной реализации:

```ts
function toArray(x: string): string[];
function toArray(x: number): number[];
function toArray(x: string | number): (string | number)[] { return [x]; }   // реализация не видна снаружи

function get(id: number): User;
function get(ids: number[]): User[];
function get(arg: number | number[]) { /* ... */ }
```

Часто вместо перегрузок лучше **generics или union** — проще поддерживать.

```ts
function first<T>(arr: readonly T[]): T | undefined { return arr[0]; }
```

Особенности:

| Тема | Пояснение |
|---|---|
| Параметр-«результат» | тип возврата выводится, но для публичного API указывайте явно |
| `void` и коллбэки | функция, возвращающая значение, совместима с типом `() => void` |
| `readonly` параметры | защита от мутации |
| Предикаты типа | `function isUser(x: unknown): x is User` |
| Assertion functions | `function assert(x: unknown): asserts x is string` |
| Ковариантность результата, контравариантность параметров | см. [[N:3ea33104867981a1b567e0d670b97106]] |

## Нюансы и подводные камни

- Порядок перегрузок важен: выбирается первая подходящая.
- Реализация должна быть совместима со всеми сигнатурами.
- `Function` как тип — небезопасен; используйте конкретные сигнатуры.
- Необязательный параметр перед обязательным недопустим.
- Стрелочные функции и `this`: нельзя типизировать `this`-параметр.

## Практика

1. Типизируйте `debounce<T extends (...a: any[]) => void>(fn: T, ms: number)`.
2. Сделайте функцию с перегрузками и перепишите на generics.
3. Напишите type predicate для проверки ответа API.

## Вопросы с ответами

> [!question]- Когда нужны перегрузки?
> Когда тип результата зависит от типа аргументов, и generics/union не выразят связь.

> [!question]- Что такое type predicate?
> Функция, возвращающая `x is T`, сужающая тип в вызывающем коде.

## Связанные темы

- [[N:3ea331048679810faa6dfaa9aee94a58]]
- [[N:3ea331048679812694a2d2a4ca78bc40]]
