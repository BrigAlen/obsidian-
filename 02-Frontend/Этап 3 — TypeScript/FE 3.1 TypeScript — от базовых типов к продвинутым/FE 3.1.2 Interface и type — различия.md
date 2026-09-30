---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981348550f303d11f5b03
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/interface, topic/type, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Interface и type: различия

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.1 Базовые типы, any, unknown, never, void|Предыдущая]] · → [[FE 3.1.3 Union, intersection, literal types|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






















> [!info] Зачем это на собесе
> Классический вопрос: «Когда `interface`, а когда `type`?»

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
interface User { id: number; name: string; email?: string; readonly createdAt: Date }
interface Admin extends User { permissions: string[] }

type Point = { x: number; y: number };
type ID = string | number;                 // только type умеет union
type Pair<T> = [T, T];
type Handler = (e: Event) => void;
```

| Возможность | `interface` | `type` |
|---|---|---|
| Описание объектов | да | да |
| Расширение | `extends`, **declaration merging** | пересечение `&` |
| Union, tuple, примитивы, mapped/conditional | нет | да |
| Реализация в классе (`implements`) | да | да (для объектных типов) |
| Слияние объявлений | да (дополнение глобальных типов, `Window`) | нет (ошибка дубликата) |
| Сообщения об ошибках, производительность | чуть лучше при глубоком наследовании | |
| Рекурсивность | да | да |

```ts
interface Window { appVersion: string }        // declaration merging: расширяем глобальный тип
interface A { a: 1 } interface A { b: 2 }      // → { a: 1; b: 2 }

type Result = { ok: true; data: string } | { ok: false; error: Error };
```

Рекомендации:

- Публичные API библиотек и объекты-контракты — `interface` (расширяемость).
- Объединения, вычисляемые типы, кортежи, утилиты — `type`.
- Главное — единообразие в команде (часто: `type` по умолчанию, `interface` для расширяемых контрактов).

## Нюансы и подводные камни

- Пересечение `&` несовместимых свойств даёт `never` для конфликтующего поля.
- `interface` нельзя описать union: `type` нужен.
- Слияние деклараций может скрыть ошибку двойного объявления.
- Оба типа проверяются **структурно**.

## Практика

1. Опишите модель заказа через `interface` и расширьте её.
2. Напишите дискриминируемый union для результата запроса.
3. Расширьте `Window` через declaration merging.

## Вопросы с ответами

> [!question]- Чем interface отличается от type?
> `interface` поддерживает слияние деклараций и `extends`, `type` — union, кортежи и вычисляемые типы.

> [!question]- Что такое declaration merging?
> Объединение нескольких объявлений одного `interface` в один тип.

## Связанные темы

- [[N:3ea3310486798159b0ccf7fe498691fa]]
- [[N:3ea33104867981d8af81c0aa8cac4d4a]]
