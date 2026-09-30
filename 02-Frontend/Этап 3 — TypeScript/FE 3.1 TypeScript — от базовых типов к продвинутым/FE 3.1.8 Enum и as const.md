---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 8
status: todo
level: middle
notion_id: 3ea33104867981b6ac0bf52e95f84990
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/enum, topic/const-assertions, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Enum и as const

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.7 Классы в TS — модификаторы, abstract, implements|Предыдущая]] · → [[FE 3.1.9 Generics|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Почему многие избегают `enum` и чем его заменяют.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
enum Direction { Up, Down }                 // числовой: 0, 1 (обратное отображение)
enum Status { Active = "active", Blocked = "blocked" }    // строковой
const enum Flags { A = 1, B = 2 }           // инлайнится, но проблемы с isolatedModules

const Roles = { admin: "admin", user: "user" } as const;      // литеральные значения, readonly
type Role = typeof Roles[keyof typeof Roles];                  // "admin" | "user"

const STATUSES = ["idle", "loading", "done"] as const;
type StatusUnion = typeof STATUSES[number];                    // "idle" | "loading" | "done"
```

| | `enum` | `as const` объект/union |
|---|---|---|
| Рантайм-код | генерирует объект | обычный объект (или ничего для union) |
| Tree shaking | хуже | лучше |
| Числовой enum | принимает любое число (небезопасно) | нет проблемы |
| Совместимость с JSON/API | требуется преобразование | значения — обычные строки |
| Сообщения/итерация | обратные отображения для числовых | `Object.values(Roles)` |
| `erasableSyntaxOnly` / Node type stripping | не поддерживается | поддерживается |

Итог: для новых проектов предпочитают **union литералов** или `as const`-объекты. Enum допустим в устоявшихся кодовых базах (Angular), но у числовых есть подводные камни.

`as const`: делает литералы точными и структуры `readonly`.

```ts
const config = { mode: "dark", sizes: [1, 2] } as const;    // { readonly mode: "dark"; readonly sizes: readonly [1, 2] }
```

## Нюансы и подводные камни

- Числовой enum позволяет присвоить любое число: `const d: Direction = 42`.
- `const enum` не работает с `isolatedModules` (Vite/esbuild) — избегайте.
- `Object.keys` числового enum возвращает и имена, и числа.
- `as const` не выполняет проверки во время выполнения.

## Практика

1. Замените `enum` статусов на `as const` объект и union.
2. Постройте тип ключей и значений из массива `as const`.
3. Получите список значений для `<select>` из `as const`.

## Вопросы с ответами

> [!question]- Почему не рекомендуют enum?
> Генерируют рантайм-код, числовые небезопасны, не поддерживаются «стираемым» синтаксисом; литеральные union проще и легче.

> [!question]- Что делает `as const`?
> Выводит самые узкие литеральные типы и делает структуру readonly.

## Связанные темы

- [[N:3ea3310486798167b6ffeadd14bf3dcd]]
- [[N:3ea331048679812d9621f339f8175cdd]]
