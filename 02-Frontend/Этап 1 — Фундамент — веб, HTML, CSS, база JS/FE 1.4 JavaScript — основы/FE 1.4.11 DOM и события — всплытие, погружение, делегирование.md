---
type: topic
domain: frontend
stage: 1
section: "1.4"
order: 11
status: todo
level: junior
notion_id: 3ea33104867981e090f1cd2ad6c856f0
tags: [domain/frontend, stage/1, level/junior, topic/javascript, topic/dom, topic/events, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# DOM и события: всплытие, погружение, делегирование

↑ [[FE 1.4 JavaScript — основы|1.4 JavaScript: основы]] · ← [[FE 1.4.10 ES6+ возможности|Предыдущая]] · → [[FE 1.4.12 Обработка ошибок|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->
























> [!info] Зачем это на собесе
> Фазы событий и делегирование — стабильный вопрос; во фреймворках понимание помогает отлаживать поведение.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**DOM** — древовидная модель документа, доступная из JS.

```js
const el = document.querySelector(".card");
document.querySelectorAll("li");        // статический NodeList
el.classList.toggle("active");
el.dataset.id;                          // data-id
el.textContent = "текст";               // безопасно (innerHTML — риск XSS)
const node = document.createElement("li"); list.append(node);
el.closest(".list"); el.matches(".x");
el.getBoundingClientRect();
```

**Фазы события**: погружение (capturing: от `window` вниз) → цель (target) → всплытие (bubbling: вверх). Слушатель по умолчанию срабатывает на всплытии.

```js
list.addEventListener("click", (e) => {
  const item = e.target.closest("[data-id]");        // делегирование: один обработчик на список
  if (!item || !list.contains(item)) return;
  select(item.dataset.id);
});
btn.addEventListener("click", handler, { once: true, passive: true });
form.addEventListener("submit", (e) => { e.preventDefault(); });
e.stopPropagation();   // остановить всплытие; stopImmediatePropagation — и другие слушатели
```

| Свойство | Смысл |
|---|---|
| `event.target` | элемент, где произошло событие |
| `event.currentTarget` | элемент с обработчиком |
| `preventDefault()` | отменить действие по умолчанию |
| `passive: true` | обещание не вызывать `preventDefault` (плавный скролл) |
| `capture: true` | слушать на погружении |

**Делегирование**: один обработчик на родителе вместо множества на потомках — экономия памяти, работает для динамически добавленных элементов.

Иные важные события: `DOMContentLoaded`, `load`, `input`, `change`, `focus/blur` (не всплывают; `focusin/out` всплывают), `scroll`, `resize`, `IntersectionObserver`, `MutationObserver`, `ResizeObserver`, `CustomEvent`.

## Нюансы и подводные камни

- Не забывайте снимать слушатели (`removeEventListener`, `AbortController`) — утечки.
- Массовые обновления DOM в цикле вызывают layout: собирайте в `DocumentFragment`, группируйте чтение и запись.
- `stopPropagation` ломает делегирование и аналитику — используйте осознанно.
- `innerHTML` с пользовательскими данными — XSS.
- Обработчики `scroll/resize` — с throttle или через Observers.

## Практика

1. Реализуйте делегирование для списка с динамическими элементами.
2. Воспроизведите всплытие и погружение, выведя порядок вызовов.
3. Подгрузите данные при прокрутке через `IntersectionObserver`.

## Вопросы с ответами

> [!question]- Что такое всплытие и погружение?
> Две фазы распространения события: от корня к цели (capturing) и от цели к корню (bubbling).

> [!question]- Что такое делегирование?
> Один обработчик на родителе, определяющий цель через `event.target`, вместо обработчиков на каждом потомке.

> [!question]- Чем `target` отличается от `currentTarget`?
> `target` — источник события, `currentTarget` — элемент, на котором сработал слушатель.

## Связанные темы

- [[N:3ea33104867981faa9bafdc336eee7fb]]
- [[N:3ea331048679816da10fe17794cbb365]]
