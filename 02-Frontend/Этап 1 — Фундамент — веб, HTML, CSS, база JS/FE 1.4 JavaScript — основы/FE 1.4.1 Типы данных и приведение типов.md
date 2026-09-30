---
type: topic
domain: frontend
stage: 1
section: "1.4"
order: 1
status: todo
level: junior
notion_id: 3ea3310486798101bb32e955dc77616f
tags: [domain/frontend, stage/1, level/junior, topic/javascript, topic/types, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Типы данных и приведение типов

↑ [[FE 1.4 JavaScript — основы|1.4 JavaScript: основы]] · → [[FE 1.4.2 Сравнение — == и ===, Object.is, NaN|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Самые популярные «странные» вопросы: `typeof null`, `[] + {}`, `"5" - 2`. Важно знать правила, а не заучивать примеры.

## Объяснение

**Примитивы** (неизменяемые, по значению): `string`, `number`, `boolean`, `null`, `undefined`, `symbol`, `bigint`. **Объекты** (по ссылке): всё остальное — массивы, функции, `Date`, `Map`.

```js
typeof 42           // "number"
typeof "a"          // "string"
typeof undefined    // "undefined"
typeof null         // "object"   ← историческая ошибка
typeof []           // "object"   → Array.isArray([])
typeof (() => 1)    // "function"
typeof 10n          // "bigint"
Number.isInteger(1.0), Number.isNaN(NaN), 0.1 + 0.2 === 0.3   // true, true, false (числа с плавающей точкой IEEE-754)
```

**Приведение типов**:

| Операция | Правило |
|---|---|
| `+` со строкой | конкатенация: `"5" + 2 = "52"` |
| `- * / %` | приводят к числу: `"5" - 2 = 3` |
| Boolean | falsy: `false, 0, -0, 0n, "", null, undefined, NaN`; всё остальное truthy (в т.ч. `[]`, `{}`, `"0"`) |
| Number(x) | `Number("")=0`, `Number(" 12 ")=12`, `Number("a")=NaN`, `Number(null)=0`, `Number(undefined)=NaN` |
| String(x) | `String(null)="null"`, `String([1,2])="1,2"` |
| Объект → примитив | через `Symbol.toPrimitive`, затем `valueOf`, `toString` |

```js
[] + {}        // "[object Object]"
[] == false    // true  ([] → "" → 0)
"5" * "2"      // 10
+"42", +"", +[]   // 42, 0, 0
!!"0", !!""    // true, false
```

## Нюансы и подводные камни

- `NaN !== NaN`: проверяйте `Number.isNaN`, а не `isNaN` (он приводит к числу).
- `Number.MAX_SAFE_INTEGER` = 2⁵³−1: для больших целых — `BigInt`.
- `parseInt("08")`, `parseInt(0.0000005)` = 5: используйте `Number()` или `parseInt(s, 10)` осознанно.
- Неявное приведение — источник багов: предпочитайте явное (`Number()`, `String()`, `Boolean()`).
- Оператор `??` реагирует только на `null/undefined`, `||` — на любые falsy.

## Практика

1. Предскажите результаты 10 выражений с `+`, `==`, `[]`, `{}`, затем проверьте в консоли.
2. Реализуйте безопасный парсинг числа из строки формы.
3. Сравните `||` и `??` на значении `0` и `""`.

## Вопросы с ответами

> [!question]- Почему `typeof null === "object"`?
> Историческая ошибка ранней реализации JS, сохранённая для совместимости.

> [!question]- Почему `0.1 + 0.2 !== 0.3`?
> Числа хранятся в двоичном формате IEEE-754; нужны сравнение с допуском или целые единицы (копейки).

> [!question]- Что такое falsy?
> `false, 0, -0, 0n, "", null, undefined, NaN`.

## Связанные темы

- [[N:3ea33104867981bc82efc791639f77c8]]
- [[N:3ea33104867981669b6bd6f060aa0c30]]
