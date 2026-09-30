---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 12
status: todo
level: middle
notion_id: 3ea3310486798141ac16e74c3bd7c467
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/performance, topic/patterns, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Debounce и throttle

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.11 Память и сборщик мусора, утечки|Предыдущая]] · → [[FE 2.1.13 Функциональное программирование — чистые функции, каррирование, иммутабельность|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Классическая задача на замыкания и таймеры; реализуют «на доске».

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| | Debounce | Throttle |
|---|---|---|
| Идея | вызвать после паузы в событиях | не чаще одного раза за интервал |
| Пример | поиск при вводе, автосохранение | скролл, resize, mousemove |
| Вызов | trailing (после паузы) | leading/trailing по периодам |

```js
function debounce(fn, delay, { leading = false } = {}) {
  let timer;
  return function debounced(...args) {
    const callNow = leading && !timer;
    clearTimeout(timer);
    timer = setTimeout(() => { timer = null; if (!leading) fn.apply(this, args); }, delay);
    if (callNow) fn.apply(this, args);
  };
}

function throttle(fn, interval) {
  let last = 0, timer, lastArgs;
  return function throttled(...args) {
    const now = Date.now(), remaining = interval - (now - last);
    lastArgs = args;
    if (remaining <= 0) { clearTimeout(timer); timer = null; last = now; fn.apply(this, args); }
    else if (!timer) timer = setTimeout(() => { last = Date.now(); timer = null; fn.apply(this, lastArgs); }, remaining);
  };
}
```

```js
input.addEventListener("input", debounce((e) => search(e.target.value), 300));
window.addEventListener("scroll", throttle(updateHeader, 100), { passive: true });
```

Во Vue: `watchDebounced`, `useDebounceFn`, `useThrottleFn` (VueUse); для запросов — отмена предыдущих (`AbortController`), в Vue Query — `keepPreviousData`.

Альтернативы: `requestAnimationFrame` для визуальных обновлений, `IntersectionObserver` вместо scroll-слушателей.

## Нюансы и подводные камни

- Debounce на общем экземпляре создаётся один раз (не внутри функции рендера) — иначе таймеры разные.
- Отмена при размонтировании компонента: `debounced.cancel()`.
- Устаревшие ответы: медленный запрос может прийти после нового — используйте отмену или сопоставление токенов.
- Слишком большая задержка портит UX.

## Практика

1. Реализуйте `debounce` с `cancel` и `flush`, `throttle` с leading/trailing.
2. Реализуйте поиск с debounce и отменой предыдущего запроса.
3. Замените scroll-слушатель на `IntersectionObserver`.

## Вопросы с ответами

> [!question]- Чем debounce отличается от throttle?
> Debounce вызывает функцию после паузы, throttle — не чаще раза за интервал.

> [!question]- Когда что использовать?
> Debounce — ввод в поиск, throttle — прокрутка и перетаскивание.

## Связанные темы

- [[N:3ea33104867981dabc74d9f55baadb88]]
- [[N:3ea33104867981c0a04de2ebb0ed17e0]]
