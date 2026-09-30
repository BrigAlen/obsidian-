---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 6
status: todo
level: middle
notion_id: 3ea331048679812694a2d2a4ca78bc40
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/narrowing, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Narrowing и type guards

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.5 Типизация функций и перегрузки|Предыдущая]] · → [[FE 3.1.7 Классы в TS — модификаторы, abstract, implements|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Сужение типов — то, как вы безопасно работаете с union и `unknown`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Narrowing** — сужение типа анализом потока управления.

| Приём | Пример |
|---|---|
| `typeof` | `typeof x === "string"` |
| `instanceof` | `x instanceof Date` |
| Проверка на `null/undefined`, truthiness | `if (x)`, `x != null`, `x ?? y` |
| `in` | `"swim" in animal` |
| Дискриминант | `s.status === "success"` |
| Равенство | `a === b` сужает пересечение типов |
| Пользовательские type guards | `x is T` |
| Assertion functions | `asserts x is T` |
| Исчерпывающая проверка | `never` |

```ts
function len(x: string | string[] | null) {
  if (x === null) return 0;
  if (typeof x === "string") return x.length;
  return x.length;                      // string[]
}

interface Cat { meow(): void } interface Dog { bark(): void }
const isCat = (a: Cat | Dog): a is Cat => "meow" in a;

function assertNever(x: never): never { throw new Error(String(x)); }
function handle(e: Event): string { switch (e.type) { case "a": return "a"; default: return assertNever(e as never); } }

function parseUser(x: unknown): User {
  if (typeof x === "object" && x !== null && "id" in x && typeof (x as any).id === "number") return x as User;
  throw new TypeError("Invalid user");
}
```

Сужение работает по потоку: после `return`/`throw`, внутри условий, в ветках `switch`. Оно сбрасывается внутри коллбэков для изменяемых переменных (`let`).

## Нюансы и подводные камни

- Кастомный type guard может «врать»: компилятор доверяет ему; проверяйте реальную структуру.
- `typeof null === "object"`: сначала проверяйте `null`.
- Сужение теряется после присваивания или в замыкании над `let`.
- `Array.isArray` сужает до `any[]`; `filter(Boolean)` не сужает без явного предиката.

## Практика

1. Напишите type guard для API-ответа и используйте в цепочке.
2. Реализуйте исчерпывающий `switch` с `never`.
3. Замените `as` на сужение в 3 местах.

## Вопросы с ответами

> [!question]- Что такое type guard?
> Проверка (встроенная или пользовательская), после которой компилятор считает тип более узким.

> [!question]- Чем `is` отличается от `asserts`?
> `is` возвращает boolean и сужает в ветке, `asserts` бросает при неверном условии и сужает после вызова.

## Связанные темы

- [[N:3ea331048679816a8d8fc767f7201f2e]]
- [[N:3ea3310486798167b6ffeadd14bf3dcd]]
