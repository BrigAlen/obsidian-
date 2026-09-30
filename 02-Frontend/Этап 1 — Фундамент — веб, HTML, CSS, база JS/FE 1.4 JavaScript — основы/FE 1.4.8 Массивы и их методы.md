---
type: topic
domain: frontend
stage: 1
section: "1.4"
order: 8
status: todo
level: junior
notion_id: 3ea33104867981f9b32fe932432f0651
tags: [domain/frontend, stage/1, level/junior, topic/javascript, topic/arrays, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Массивы и их методы

↑ [[FE 1.4 JavaScript — основы|1.4 JavaScript: основы]] · ← [[FE 1.4.7 Объекты — копирование, сравнение, дескрипторы|Предыдущая]] · → [[FE 1.4.9 Строки и регулярные выражения|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

















> [!info] Зачем это на собесе
> Ежедневный инструмент; на интервью просят реализовать `map/filter/reduce` и знать, какие методы мутируют.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Категория | Методы |
|---|---|
| Преобразование (новый массив) | `map`, `filter`, `slice`, `concat`, `flat`, `flatMap`, `toSorted`, `toReversed`, `toSpliced`, `with` |
| Свёртка | `reduce`, `reduceRight` |
| Поиск | `find`, `findIndex`, `findLast`, `indexOf`, `includes`, `some`, `every` |
| Мутирующие | `push`, `pop`, `shift`, `unshift`, `splice`, `sort`, `reverse`, `fill` |
| Прочее | `Array.from`, `Array.of`, `Array.isArray`, `at`, `join`, `entries/keys/values` |

```js
const orders = [{ id: 1, total: 100, paid: true }, { id: 2, total: 50, paid: false }];
orders.filter(o => o.paid).map(o => o.total);                     // [100]
orders.reduce((sum, o) => sum + o.total, 0);                      // 150
Object.groupBy(orders, o => o.paid ? "paid" : "open");            // { paid: [...], open: [...] }
[...new Set([1, 2, 2, 3])];                                       // уникальные
[3, 1, 10].sort();               // [1, 10, 3] — по умолчанию строки!
[3, 1, 10].sort((a, b) => a - b);                                 // [1, 3, 10]
const copy = [...arr].sort();     // не мутируя (или toSorted)
Array.from({ length: 5 }, (_, i) => i * 2);                       // [0,2,4,6,8]
```

Сложность: `push/pop` O(1), `shift/unshift` O(n), `includes/indexOf` O(n), `sort` O(n log n).

Итерация: `for...of`, `forEach` (нельзя прервать; `break` невозможен), `for` (быстрее и с `await`), `some/every` для прерывания.

## Нюансы и подводные камни

- `sort` без компаратора сортирует как строки и мутирует массив.
- `map` с `async` возвращает массив промисов: `await Promise.all(arr.map(...))`.
- `forEach` не ждёт `await` внутри.
- `arr.length = 0` очищает массив; `delete arr[i]` создаёт «дыру».
- `reduce` без начального значения на пустом массиве бросает ошибку.
- Изменение массива во время перебора приводит к пропускам.

## Практика

1. Реализуйте свои `map`, `filter`, `reduce`, `flat`.
2. Сгруппируйте заказы по клиенту и посчитайте суммы через `reduce`.
3. Уберите дубликаты по ключу объекта.

## Вопросы с ответами

> [!question]- Какие методы массива мутируют его?
> `push`, `pop`, `shift`, `unshift`, `splice`, `sort`, `reverse`, `fill`; у новых версий есть неизменяющие аналоги `toSorted` и др.

> [!question]- Чем `map` отличается от `forEach`?
> `map` возвращает новый массив результатов, `forEach` — ничего.

> [!question]- Почему `[10, 9, 1].sort()` даёт `[1, 10, 9]`?
> Сортировка по умолчанию сравнивает элементы как строки.

## Связанные темы

- [[N:3ea33104867981228603ca7fc9b662f2]]
- [[N:3ea33104867981188cebc5c86e255835]]
