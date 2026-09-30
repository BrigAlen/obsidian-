---
type: topic
domain: frontend
stage: 1
section: "1.4"
order: 2
status: todo
level: junior
notion_id: 3ea33104867981669b6bd6f060aa0c30
tags: [domain/frontend, stage/1, level/junior, topic/javascript, topic/equality, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Сравнение: == и ===, Object.is, NaN

↑ [[FE 1.4 JavaScript — основы|1.4 JavaScript: основы]] · ← [[FE 1.4.1 Типы данных и приведение типов|Предыдущая]] · → [[FE 1.4.3 var, let, const, hoisting, TDZ|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Классика: чем `==` отличается от `===` и что делает `Object.is`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Оператор | Поведение |
|---|---|
| `===` (строгое) | без приведения типов: типы разные — `false` |
| `==` (нестрогое) | с приведением типов по алгоритму Abstract Equality |
| `Object.is(a, b)` | как `===`, но `NaN` равен `NaN`, а `+0` не равен `-0` |
| `Array.includes` | использует SameValueZero (`NaN` найдёт, `+0 == -0`) |

Правила `==`:

- `null == undefined` — `true`, и больше ни с чем не равны.
- Число и строка → строка в число.
- Boolean → число (`true` = 1).
- Объект и примитив → объект в примитив.

```js
0 == "0"       // true
0 == ""        // true
"0" == ""      // false (нетранзитивно!)
null == 0      // false
null == undefined  // true
NaN === NaN    // false
Object.is(NaN, NaN)  // true
Object.is(0, -0)     // false
[1] == 1       // true
{} == {}       // false (разные ссылки)
```

Объекты сравниваются **по ссылке**: `{a:1} === {a:1}` — `false`. Глубокое сравнение — вручную, `structuredClone` + `JSON.stringify` (ограниченно) или библиотеки (`lodash.isEqual`).

Рекомендация: всегда `===`. Исключение: `x == null` для проверки на `null` **и** `undefined`.

## Нюансы и подводные камни

- `==` нетранзитивно: `"0" == false`, `false == ""`, но `"0" != ""`.
- `NaN` проверять через `Number.isNaN`/`Object.is`.
- `-0` в вычислениях: `1 / -0 = -Infinity`.
- `switch` использует строгое сравнение.
- Сравнение дат: `date1 === date2` — ссылки; используйте `getTime()`.

## Практика

1. Составьте таблицу 8×8 результатов `==` для разных значений и сравните с ожиданиями.
2. Реализуйте `deepEqual` для объектов и массивов.
3. Найдите в коде `==` и решите, что заменить.

## Вопросы с ответами

> [!question]- Чем `==` отличается от `===`?
> `==` приводит типы перед сравнением, `===` сравнивает без приведения.

> [!question]- Что делает `Object.is`?
> Сравнивает как `===`, но считает `NaN` равным `NaN` и различает `+0` и `-0`.

> [!question]- Когда `x == null` допустимо?
> Когда нужно проверить одновременно `null` и `undefined`.

## Связанные темы

- [[N:3ea3310486798101bb32e955dc77616f]]
- [[N:3ea33104867981dc8665de8df9c3f74d]]
