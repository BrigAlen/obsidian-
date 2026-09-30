---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 10
status: todo
level: middle
notion_id: 3ea3310486798168bdb7c7a21246f521
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/type-operators, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# keyof, typeof, indexed access

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.9 Generics|Предыдущая]] · → [[FE 3.1.11 Mapped и conditional types, infer|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Операторы типов — основа построения производных типов из данных и других типов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
interface User { id: number; name: string; tags: string[]; address: { city: string } }

type UserKey = keyof User;                       // "id" | "name" | "tags" | "address"
type IdType = User["id"];                        // number
type City = User["address"]["city"];             // string
type Tag = User["tags"][number];                 // string — тип элемента массива
type Values = User[keyof User];                  // union всех значений

const config = { host: "localhost", port: 3000 };
type Config = typeof config;                     // { host: string; port: number }
type ConfigKey = keyof typeof config;            // "host" | "port"

const ROLES = ["admin", "user"] as const;
type Role = (typeof ROLES)[number];              // "admin" | "user"

function getProp<T, K extends keyof T>(o: T, k: K): T[K] { return o[k]; }
type Fn = () => Promise<string>;  type Res = Awaited<ReturnType<Fn>>;   // string
```

| Оператор | Действие |
|---|---|
| `keyof T` | union ключей |
| `typeof x` (в позиции типа) | тип значения `x` |
| `T[K]` | тип свойства (indexed access) |
| `T[number]` | тип элемента массива/кортежа |
| `T[keyof T]` | значения объекта |

Отличие `typeof` в типах от `typeof` в JS: первый работает во время компиляции.

## Нюансы и подводные камни

- `keyof` с индексной сигнатурой `{ [k: string]: X }` даёт `string | number`.
- `typeof` можно применять только к идентификаторам и их свойствам.
- `Object.keys(obj)` типизирован как `string[]` — используйте приведение или обёртку `keys<T>()`.
- Получение типов из значений уменьшает дублирование, но привязывает типы к реализации.

## Практика

1. Из массива `as const` получите union и функцию `isRole`.
2. Напишите `getProp` с `keyof`.
3. Выведите тип API-клиента из объекта функций через `typeof`.

## Вопросы с ответами

> [!question]- Что делает `keyof`?
> Возвращает union ключей типа.

> [!question]- Как получить тип элемента массива?
> `T[number]`.

## Связанные темы

- [[N:3ea331048679812d9621f339f8175cdd]]
- [[N:3ea331048679816495f6eb1b9f2919b0]]
