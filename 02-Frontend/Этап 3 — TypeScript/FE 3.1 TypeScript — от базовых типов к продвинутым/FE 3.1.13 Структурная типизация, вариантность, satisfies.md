---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 13
status: todo
level: middle
notion_id: 3ea33104867981a1b567e0d670b97106
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/structural-typing, topic/variance, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Структурная типизация, вариантность, satisfies

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.12 Template literal types|Предыдущая]] · → [[FE 3.1.14 Декораторы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Почему TS совместим по «форме» и что такое ко/контравариантность, `satisfies`.

## Объяснение

**Структурная типизация**: типы совместимы, если структура подходит; имена не важны («утиная типизация» на этапе компиляции).

```ts
interface Point { x: number; y: number }
const p = { x: 1, y: 2, z: 3 };
const q: Point = p;              // ок: лишнее свойство допустимо для переменной
const r: Point = { x: 1, y: 2, z: 3 };   // ошибка: excess property check только для литералов
```

**Номинальность** имитируют «брендами»:

```ts
type UserId = string & { readonly __brand: "UserId" };
const asUserId = (s: string) => s as UserId;
function load(id: UserId) {}
// load("abc");   // ошибка — обычная строка не подходит
```

**Вариантность**:

| Позиция | Вариантность | Пример |
|---|---|---|
| Результат функции | ковариантна | `() => Dog` подходит вместо `() => Animal` |
| Параметр функции | контравариантна (`strictFunctionTypes`) | `(a: Animal) => void` подходит вместо `(d: Dog) => void` |
| Массивы, свойства | ковариантны (небезопасно, но допущено) | `Dog[]` → `Animal[]` |
| Методы (bivariance) | двувариантны | исключение для обратной совместимости |

Модификаторы вариантности в generics: `in` / `out` (TS 4.7).

**`satisfies`** (4.9): проверяет соответствие типу, не расширяя выведенный тип.

```ts
const routes = { home: "/", user: "/u/:id" } satisfies Record<string, string>;
routes.home;           // тип "/" сохраняется (при аннотации Record<string,string> стал бы string)

const palette = { red: [255, 0, 0], green: "#00ff00" } satisfies Record<string, string | number[]>;
palette.red.map(x => x);     // известно, что red — массив
```

## Нюансы и подводные камни

- Excess property check срабатывает только на «свежих» литералах.
- Ковариантность массивов даёт дыру: `Animal[]` может принять `Cat`, записанный в массив `Dog`.
- Брендированные типы не защищают в рантайме.
- `satisfies` не изменяет тип, лишь проверяет.

## Практика

1. Создайте бренд для `UserId`/`OrderId`, чтобы их нельзя перепутать.
2. Замените аннотацию на `satisfies` в конфиге и сравните выведенные типы.
3. Воспроизведите ошибку контравариантности параметра коллбэка.

## Вопросы с ответами

> [!question]- Что такое структурная типизация?
> Совместимость типов определяется формой, а не именем или объявлением.

> [!question]- Чем `satisfies` отличается от аннотации типа?
> Проверяет соответствие типу, но сохраняет более точный выведенный тип значения.

## Связанные темы

- [[N:3ea33104867981b59058cb6474a9b446]]
- [[N:3ea331048679814d8d16e9408e1b696e]]
