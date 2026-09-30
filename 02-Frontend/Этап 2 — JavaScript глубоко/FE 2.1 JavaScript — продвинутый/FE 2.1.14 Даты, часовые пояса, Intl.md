---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 14
status: todo
level: middle
notion_id: 3ea331048679819ab2eff856ad1072b9
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/dates, topic/intl, topic/i18n, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Даты, часовые пояса, Intl

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.13 Функциональное программирование — чистые функции, каррирование, иммутабельность|Предыдущая]] · → [[FE 2.1.15 Задачи на JS — замыкания, this, Event Loop|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




















> [!info] Зачем это на собесе
> Работа с датами и локалями — источник реальных багов; ждут знания хранения UTC и `Intl`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`Date` хранит момент времени как миллисекунды от 1970-01-01 UTC; отображение зависит от часового пояса окружения.

```js
const d = new Date("2025-06-12T10:00:00Z");     // ISO 8601 с Z — UTC
d.getTime(); d.toISOString();                   // "2025-06-12T10:00:00.000Z"
new Date(2025, 5, 12);                          // месяцы с 0! (июнь = 5)
new Date("2025-06-12");                         // UTC-полночь; "2025-06-12T00:00" — локальное время (различие!)
Date.now(); d.getTimezoneOffset();
```

**Правила**: хранить и передавать время в **UTC (ISO 8601)**, показывать в часовом поясе пользователя; календарные даты без времени (день рождения) хранить как строку `YYYY-MM-DD`, а не момент времени.

**Intl** — форматирование по локали:

```js
new Intl.DateTimeFormat("ru-RU", { dateStyle: "long", timeStyle: "short", timeZone: "Europe/Moscow" }).format(d);
new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB" }).format(1234.5);   // "1 234,50 ₽"
new Intl.RelativeTimeFormat("ru", { numeric: "auto" }).format(-1, "day");                 // "вчера"
new Intl.PluralRules("ru").select(5);                                                     // "many"
new Intl.ListFormat("ru", { type: "conjunction" }).format(["a", "b", "c"]);
["ä", "a", "z"].sort(new Intl.Collator("de").compare);
```

Библиотеки: **date-fns**, **Luxon**, **Day.js** (легковесные, `Moment` устарел). Новый стандарт **Temporal** (неизменяемые типы `Instant`, `ZonedDateTime`, `PlainDate`) — поддержка появляется.

Часовые пояса: IANA-названия (`Europe/Moscow`), а не смещения; переход на летнее время делает день 23/25-часовым; на бэкенде тоже UTC.

## Нюансы и подводные камни

- `new Date("2025-06-12")` и `"2025-06-12T00:00"` интерпретируются по-разному.
- Месяцы нумеруются с 0.
- Сложение «+ 24 часа» не равно «следующий день» при смене времени.
- `toLocaleString` без явной локали и пояса даёт разные результаты на разных машинах: в тестах указывайте явно.
- Сравнение дат: `getTime()`, не `===`.
- Формат чисел с запятой/точкой зависит от локали — не парсите пользовательские числа `parseFloat`-ом слепо.

## Практика

1. Отобразите серверное UTC-время в поясе пользователя и в поясе клиники.
2. Реализуйте «сколько прошло» через `RelativeTimeFormat`.
3. Напишите тесты дат с фиксированным часовым поясом и фейковыми таймерами.

## Вопросы с ответами

> [!question]- В каком формате хранить время?
> В UTC (ISO 8601), локальное время — только для отображения.

> [!question]- Зачем Intl?
> Корректное форматирование дат, чисел, множественных чисел и сортировки по локали без ручных таблиц.

## Связанные темы

- [[N:3ea33104867981c0a04de2ebb0ed17e0]]
- [[N:3ea331048679815f9d17e64def8d245c]]
