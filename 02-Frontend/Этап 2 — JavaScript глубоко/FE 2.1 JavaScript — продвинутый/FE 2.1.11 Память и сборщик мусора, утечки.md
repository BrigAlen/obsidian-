---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 11
status: todo
level: middle
notion_id: 3ea33104867981dabc74d9f55baadb88
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/memory, topic/gc, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Память и сборщик мусора, утечки

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.10 Proxy и Reflect|Предыдущая]] · → [[FE 2.1.12 Debounce и throttle|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Утечки памяти в SPA — частая проблема; ждут перечня причин и способов найти.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Память управляется автоматически. Алгоритм GC — **mark-and-sweep**: от корней (глобальный объект, стек, активные замыкания) помечаются достижимые объекты; остальные удаляются. Циклические ссылки не мешают освобождению. Современный V8 — поколенческий (young/old), инкрементальный и параллельный GC.

**Утечка** — объекты, ставшие ненужными, но остающиеся достижимыми.

| Причина | Пример | Решение |
|---|---|---|
| Глобальные переменные | случайное присваивание без объявления | `strict mode`, линтер |
| Забытые таймеры | `setInterval` без `clearInterval` | очистка в `unmounted` |
| Слушатели событий | `addEventListener` без снятия; слушатели на `window`/`document` | `removeEventListener`, `AbortController` |
| Замыкания | удерживают большие объекты | обнулять ссылки, не захватывать лишнее |
| Отсоединённые DOM-узлы | ссылка в JS на удалённый элемент | `null`, `WeakRef`/`WeakMap` |
| Неограниченные кэши, стор | накопление без вытеснения | LRU, лимиты, TTL |
| Подписки (RxJS, WebSocket, EventBus) | не отписались | отписка в `onUnmounted` |
| Сторонние библиотеки | инстансы карт/графиков не уничтожены | `destroy()` |

```js
// Vue
onMounted(() => { timer = setInterval(tick, 1000); window.addEventListener("resize", onResize); });
onUnmounted(() => { clearInterval(timer); window.removeEventListener("resize", onResize); });

const ctrl = new AbortController();
window.addEventListener("scroll", onScroll, { signal: ctrl.signal });   // ctrl.abort() снимает
```

**Диагностика** (Chrome DevTools → Memory): снимки кучи (Heap snapshot) до/после действия и сравнение (Comparison), «Allocation instrumentation on timeline», вкладка Performance → флажок Memory, поиск Detached DOM nodes. Признак утечки: пилообразный график, не возвращающийся к базовой линии.

## Нюансы и подводные камни

- `WeakRef` и `FinalizationRegistry` не гарантируют время очистки; используйте редко.
- Большие `ArrayBuffer`/`Blob` освобождаются не сразу: `URL.revokeObjectURL`.
- SPA живёт часами: небольшая утечка накапливается.
- Утечки часто связаны с компонентами, которые не размонтируются (кэш `KeepAlive`).

## Практика

1. Воспроизведите утечку через таймер и найдите её в Heap snapshot.
2. Сравните два снимка после открытия/закрытия модального окна 20 раз.
3. Добавьте очистку в `onUnmounted` для всех подписок.

## Вопросы с ответами

> [!question]- Как работает сборщик мусора?
> Помечает достижимые от корней объекты и удаляет недостижимые (mark-and-sweep).

> [!question]- Какие бывают утечки в SPA?
> Таймеры, слушатели, замыкания, отсоединённые DOM-узлы, неограниченные кэши, забытые подписки.

## Связанные темы

- [[N:3ea331048679817da316ca0ef842cabc]]
- [[N:3ea3310486798141ac16e74c3bd7c467]]
