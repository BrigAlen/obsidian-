---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981d8af81c0aa8cac4d4a
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/union, topic/literals, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Union, intersection, literal types

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.2 Interface и type — различия|Предыдущая]] · → [[FE 3.1.4 Utility types|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->











> [!info] Зачем это на собесе
> Дискриминируемые объединения — основной приём моделирования состояний в TS.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Union** `A | B` — значение одного из типов. **Intersection** `A & B` — значение, удовлетворяющее обоим.

```ts
type Status = "idle" | "loading" | "success" | "error";       // литеральные типы
type Id = string | number;
type Timestamps = { createdAt: Date } ; type Named = { name: string };
type Entity = Named & Timestamps;                             // все поля обоих

// Дискриминируемое объединение (tagged union)
type State =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: Order[] }
  | { status: "error"; error: Error };

function render(s: State) {
  switch (s.status) {
    case "success": return s.data.length;        // здесь s: { status: "success"; data }
    case "error":   return s.error.message;
    default:        return 0;
  }
}
```

Литералы: строковые, числовые, булевы; шаблонные типы. Расширение литералов: `let x = "a"` → `string`, `const x = "a"` → `"a"`; фиксировать — `as const`.

Union и доступ к свойствам: доступны только общие для всех вариантов свойства; остальные — после сужения.

Пересечение объектных типов с конфликтующими полями даёт `never` для поля (например, `{a: string} & {a: number}`).

Моделируйте невозможные состояния невозможными: вместо `{ loading: boolean; data?: T; error?: Error }` используйте tagged union.

## Нюансы и подводные камни

- Union функций требует пересечения параметров.
- `Partial` вместо union скрывает допустимые комбинации.
- Дискриминант должен быть литеральным типом.
- Исчерпывающая проверка через `never` в `default`.

## Практика

1. Переделайте состояние загрузки с булевыми флагами на tagged union.
2. Добавьте проверку полноты `switch`.
3. Опишите API-ответ `ok/error` как union.

## Вопросы с ответами

> [!question]- Что такое discriminated union?
> Объединение объектных типов с общим литеральным полем-дискриминантом, по которому TS сужает тип.

> [!question]- Что даёт `A & B`?
> Тип со всеми свойствами обоих; при конфликте типов свойство становится `never`.

## Связанные темы

- [[N:3ea33104867981348550f303d11f5b03]]
- [[N:3ea331048679810faa6dfaa9aee94a58]]
