---
type: topic
domain: frontend
stage: 5
section: "5.1"
order: 7
status: todo
level: middle
notion_id: 3ea3310486798159bab5eadb755f6602
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/router, topic/scroll, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Scroll behavior

↑ [[FE 5.1 Vue Router|5.1 Vue Router]] · ← [[FE 5.1.6 Lazy loading маршрутов|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

















> [!info] Зачем это на собесе
> Небольшая, но заметная UX-деталь: сохранение позиции при «назад» и прокрутка к якорям.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition;                           // «назад/вперёд» — вернуть позицию
    if (to.hash) return { el: to.hash, behavior: "smooth", top: 80 };  // якорь с отступом под шапку
    if (to.path === from.path) return false;                           // смена query — не прокручивать
    return { top: 0 };                                                 // новая страница — вверх
  },
});

// Ожидание рендера/загрузки данных перед прокруткой
scrollBehavior: () => new Promise((resolve) => setTimeout(() => resolve({ top: 0 }), 300)),
```

Особенности:

- Работает только в режимах history (не в hash без History API).
- Возвращаемое значение: координаты `{ top, left }`, `{ el, top }`, `savedPosition` или `false`.
- Может быть асинхронным: дождитесь появления контента (`await nextTick()`), иначе прокрутка произойдёт до отрисовки.
- Прокрутка внутри вложенных контейнеров (не `window`) роутер не выполняет — управляйте вручную (`watch(route)` и `el.scrollTo`).
- Сохранение позиции для длинных списков с ленивой загрузкой: восстановите после загрузки данных, либо кэшируйте страницу через `KeepAlive`.

Доступность: при переходе в SPA фокус остаётся на прошлом элементе — переносите фокус на заголовок страницы (`h1`) и объявляйте смену страницы (`aria-live`), чтобы скринридеры понимали навигацию.

```ts
router.afterEach(async () => { await nextTick(); document.querySelector<HTMLElement>("h1")?.focus(); });
```

## Нюансы и подводные камни

- Данные загружаются позже DOM — сохранённая позиция может не восстановиться.
- Якорные ссылки не работают, если элемента ещё нет.
- Фиксированная шапка перекрывает целевой элемент — добавляйте `top` и `scroll-margin-top`.
- Использование `overflow` контейнера вместо `window` ломает стандартную логику.

## Практика

1. Настройте `scrollBehavior` с якорями и «назад».
2. Перенесите фокус на заголовок после навигации.
3. Восстановите позицию длинного списка после возврата.

## Вопросы с ответами

> [!question]- Как сохранить позицию прокрутки при возврате?
> Использовать `savedPosition` в `scrollBehavior` (с ожиданием отрисовки данных).

> [!question]- Что происходит с фокусом при SPA-навигации?
> Остаётся на прошлом элементе; для доступности его переносят на заголовок новой страницы.

## Связанные темы

- [[N:3ea331048679813ebd28c2768696b2fc]]
- [[N:3ea33104867981c4bc74e169ee2b8199]]
