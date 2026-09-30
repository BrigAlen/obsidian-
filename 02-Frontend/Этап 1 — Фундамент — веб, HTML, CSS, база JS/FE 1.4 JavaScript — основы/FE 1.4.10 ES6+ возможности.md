---
type: topic
domain: frontend
stage: 1
section: "1.4"
order: 10
status: todo
level: junior
notion_id: 3ea33104867981faa9bafdc336eee7fb
tags: [domain/frontend, stage/1, level/junior, topic/javascript, topic/es6, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# ES6+ возможности

↑ [[FE 1.4 JavaScript — основы|1.4 JavaScript: основы]] · ← [[FE 1.4.9 Строки и регулярные выражения|Предыдущая]] · → [[FE 1.4.11 DOM и события — всплытие, погружение, делегирование|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Современный синтаксис: ожидают свободного владения деструктуризацией, spread, `?.`, `??`, модулями.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Возможность | Пример |
|---|---|
| `let/const`, стрелки | `const f = (a) => a * 2` |
| Шаблонные строки | `` `Привет, ${name}` `` |
| Деструктуризация | `const { a, b: { c = 1 } = {}, ...rest } = obj; const [x, , y = 0] = arr;` |
| Spread / rest | `[...a, ...b]`, `{ ...o, x: 1 }`, `function f(...args)` |
| Параметры по умолчанию | `function f(a, b = a * 2)` |
| Короткая запись, вычисляемые ключи | `{ name, [key]: 1, method() {} }` |
| Классы, `#private`, `static`, геттеры | `class A { #x = 1; static create() {} }` |
| Модули | `import { a } from "./a.js"`, `export default` |
| Promise, async/await | асинхронный код |
| Итераторы, генераторы, `for...of` | обход коллекций |
| `Map`, `Set`, `WeakMap`, `Symbol`, `BigInt` | новые структуры |
| Optional chaining, nullish | `a?.b?.[0]?.()`, `x ?? "default"` |
| Логические присваивания | `a ||= 1`, `a ??= 1`, `a &&= 1` |
| `Array.at`, `Object.hasOwn`, `structuredClone`, `Array.toSorted` | новые методы |
| Top-level await | в модулях |
| `Intl`, `Temporal` (в разработке) | локали и даты |

```js
const { data: orders = [], error } = await api.get("/orders");
const total = orders.reduce((s, { price, qty = 1 }) => s + price * qty, 0);
user?.address?.street ?? "Не указано";
const merged = { ...defaults, ...options };   // порядок важен: последний побеждает
```

## Нюансы и подводные камни

- `?.` возвращает `undefined`, а не бросает ошибку: не маскируйте им реальные ошибки.
- `??` не срабатывает на `0` и `""`, в отличие от `||`.
- Деструктуризация с `null` бросает `TypeError`; значения по умолчанию срабатывают только на `undefined`.
- Spread копирует поверхностно.
- Приватные поля `#x` недоступны снаружи и в `JSON.stringify`.

## Практика

1. Перепишите старый ES5-код на современный синтаксис.
2. Используйте деструктуризацию параметров и значения по умолчанию в API-обёртке.
3. Проверьте совместимость (browserslist, caniuse) и транспиляцию Babel/esbuild.

## Вопросы с ответами

> [!question]- Что делают `?.` и `??`?
> `?.` безопасно обращается к свойствам цепочки, `??` даёт значение по умолчанию только для `null/undefined`.

> [!question]- Чем rest отличается от spread?
> Rest собирает аргументы/элементы в массив, spread раскрывает итерируемое.

## Связанные темы

- [[N:3ea33104867981188cebc5c86e255835]]
- [[N:3ea33104867981e090f1cd2ad6c856f0]]
