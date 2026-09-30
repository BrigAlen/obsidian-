---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 4
status: todo
level: middle
notion_id: 3ea331048679810faa6dfaa9aee94a58
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/utility-types, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Utility types

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.3 Union, intersection, literal types|Предыдущая]] · → [[FE 3.1.5 Типизация функций и перегрузки|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Встроенные преобразователи типов экономят код; спрашивают `Partial`, `Pick`, `Omit`, `Record`, `ReturnType`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Утилита | Результат |
|---|---|
| `Partial<T>` | все поля необязательные |
| `Required<T>` | все поля обязательные |
| `Readonly<T>` | все поля только для чтения |
| `Pick<T, K>` | подмножество полей |
| `Omit<T, K>` | без указанных полей |
| `Record<K, V>` | объект с ключами `K` и значениями `V` |
| `Exclude<U, E>` / `Extract<U, E>` | убрать / оставить члены union |
| `NonNullable<T>` | без `null` и `undefined` |
| `ReturnType<F>` / `Parameters<F>` | тип результата / параметров функции |
| `Awaited<T>` | тип после `await` (разворачивает Promise) |
| `InstanceType<C>`, `ConstructorParameters<C>` | для классов |
| `NoInfer<T>` | запрет вывода параметра типа |

```ts
interface User { id: number; name: string; email: string; role: "admin" | "user" }

type UpdateUserDto = Partial<Omit<User, "id">>;
type UserPreview = Pick<User, "id" | "name">;
type RolesMap = Record<User["role"], string[]>;
type Roles = Exclude<User["role"], "admin">;                 // "user"

async function load() { return { ok: true, items: [1, 2] }; }
type LoadResult = Awaited<ReturnType<typeof load>>;          // { ok: boolean; items: number[] }

const routes = { home: "/", user: "/u/:id" } as const;
type RouteName = keyof typeof routes;                        // "home" | "user"
```

Комбинируйте утилиты для форм, DTO и обновлений. Свои утилиты строятся на mapped/conditional types (см. [[N:3ea331048679816495f6eb1b9f2919b0]]).

## Нюансы и подводные камни

- `Omit` не проверяет существование ключа (принимает любую строку) — используйте собственную строгую версию.
- `Partial` — мелкая (shallow), вложенные объекты остаются полными: нужен `DeepPartial`.
- `Readonly` действует только на уровне компиляции.
- `Record<string, T>` не защищает от обращения к отсутствующему ключу (`noUncheckedIndexedAccess`).

## Практика

1. Из `User` постройте типы для создания, обновления и публичного профиля.
2. Реализуйте `DeepPartial`, `Mutable`, `Nullable<T>`.
3. Получите тип элемента массива из типа API-ответа.

## Вопросы с ответами

> [!question]- Чем `Pick` отличается от `Omit`?
> `Pick` выбирает перечисленные поля, `Omit` исключает их.

> [!question]- Зачем `Awaited<ReturnType<...>>`?
> Получить тип результата async-функции, а не `Promise<...>`.

## Связанные темы

- [[N:3ea33104867981d8af81c0aa8cac4d4a]]
- [[N:3ea331048679816a8d8fc767f7201f2e]]
