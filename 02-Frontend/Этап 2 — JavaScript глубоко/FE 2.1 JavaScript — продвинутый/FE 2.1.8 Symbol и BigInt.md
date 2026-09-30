---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 8
status: todo
level: middle
notion_id: 3ea331048679816aba5dc2f30dead79a
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/symbol, topic/bigint, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Symbol и BigInt

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.7 Map, Set, WeakMap, WeakSet|Предыдущая]] · → [[FE 2.1.9 Итераторы и генераторы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















> [!info] Зачем это на собесе
> Редкие типы, но вопросы «зачем Symbol» и «как хранить большие числа» встречаются.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Symbol** — уникальный неизменяемый идентификатор.

```js
const id = Symbol("id");
const user = { name: "A", [id]: 1 };       // ключ-символ: не виден в Object.keys/JSON
Symbol("x") === Symbol("x");               // false
Symbol.for("app.key") === Symbol.for("app.key");   // true: глобальный реестр
```

Применения: «скрытые» свойства без конфликтов имён, метки, метапрограммирование через **well-known symbols**:

| Символ | Назначение |
|---|---|
| `Symbol.iterator` | делает объект итерируемым (`for...of`, spread) |
| `Symbol.asyncIterator` | асинхронная итерация |
| `Symbol.toPrimitive` | преобразование в примитив |
| `Symbol.toStringTag` | `Object.prototype.toString` |
| `Symbol.hasInstance` | поведение `instanceof` |

**BigInt** — целые произвольной точности (суффикс `n`).

```js
const big = 2n ** 64n;             // 18446744073709551616n
9007199254740993n + 1n;            // точно, в отличие от Number
BigInt(123); Number(5n); typeof 1n;   // "bigint"
1n + 1;                            // TypeError: смешивать с Number нельзя
5n / 2n;                           // 2n (целочисленное деление)
```

Применения: идентификаторы (Snowflake, id > 2⁵³), криптография, деньги в минимальных единицах.

## Нюансы и подводные камни

- `JSON.stringify` не поддерживает BigInt (бросает ошибку) — сериализуйте вручную.
- `Math.*` не работает с BigInt.
- Символ-ключи не попадают в `for...in`, `Object.keys`, JSON (используйте `Object.getOwnPropertySymbols`).
- Сравнение `1n == 1` — `true`, `1n === 1` — `false`.
- Идентификаторы, приходящие с сервера как числа > 2⁵³, теряют точность — передавайте строкой.

## Практика

1. Сделайте объект итерируемым через `Symbol.iterator`.
2. Сохраните id заказа > 2⁵³ без потери точности.
3. Реализуйте «приватное» свойство на символе.

## Вопросы с ответами

> [!question]- Зачем нужен Symbol?
> Создавать уникальные ключи без коллизий и настраивать поведение языка (well-known symbols).

> [!question]- Когда нужен BigInt?
> Для целых, превышающих безопасный диапазон `Number` (2⁵³−1).

## Связанные темы

- [[N:3ea33104867981bbab02d2b18bd7ffe9]]
- [[N:3ea33104867981e6b8fdfbbecd2a548e]]
