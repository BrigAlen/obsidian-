---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 9
status: todo
level: middle
notion_id: 3ea331048679812d9621f339f8175cdd
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/generics, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Generics

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.8 Enum и as const|Предыдущая]] · → [[FE 3.1.10 keyof, typeof, indexed access|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Generics — ключ к переиспользуемому типобезопасному коду; ждут ограничений, значений по умолчанию и вывода.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Параметры типа позволяют писать код независимо от конкретного типа с сохранением связей.

```ts
function identity<T>(x: T): T { return x; }
identity("a");                 // T = string (вывод)
identity<number>(1);

function pluck<T, K extends keyof T>(obj: T, key: K): T[K] { return obj[key]; }     // ограничение

interface ApiResponse<T = unknown> { data: T; error?: string }
type Paginated<T> = { items: T[]; total: number };

class Repo<T extends { id: number }> {
  private items = new Map<number, T>();
  add(item: T) { this.items.set(item.id, item); }
  get(id: number): T | undefined { return this.items.get(id); }
}

async function request<T>(url: string): Promise<T> { const r = await fetch(url); return r.json() as Promise<T>; }
const users = await request<User[]>("/api/users");       // T нельзя проверить в рантайме!
```

| Возможность | Пример |
|---|---|
| Ограничения | `T extends { id: number }` |
| Значения по умолчанию | `<T = string>` |
| Несколько параметров | `<K, V>` |
| `keyof` | `K extends keyof T` |
| `const` параметры (5.0) | `<const T>` сохраняет литералы |
| Условные типы | `T extends string ? A : B` |
| Вывод | из аргументов; можно задать явно |

Правило: параметр типа должен использоваться в сигнатуре минимум **дважды** (связывать вход и выход), иначе он лишний.

## Нюансы и подводные камни

- `request<T>` не проверяет данные: `T` — обещание. Для безопасности — runtime-валидация (см. [[N:cf701e59e7894adfb9428fd9c9678d93]]).
- Слишком общие generics ухудшают читаемость: ограничивайте `extends`.
- Стирание типов: нельзя `new T()` или `typeof T` в рантайме.
- Дефолт `T = any` — плохой выбор.
- Контекстный вывод может выбрать неожиданный тип: указывайте явно.

## Практика

1. Напишите `groupBy<T, K extends PropertyKey>(arr: T[], key: (x: T) => K)`.
2. Типизируйте `useAsync<T>` composable.
3. Сделайте generic `Result<T, E>`.

## Вопросы с ответами

> [!question]- Зачем generics?
> Писать переиспользуемый код, сохраняя связь типов входа и выхода.

> [!question]- Что значит `T extends keyof U`?
> Ограничение: `T` должен быть одним из ключей типа `U`.

## Связанные темы

- [[N:3ea33104867981b6ac0bf52e95f84990]]
- [[N:3ea3310486798168bdb7c7a21246f521]]
