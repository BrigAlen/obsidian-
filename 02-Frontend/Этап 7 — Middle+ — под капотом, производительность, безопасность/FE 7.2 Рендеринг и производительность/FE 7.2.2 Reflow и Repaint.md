---
type: topic
domain: frontend
stage: 7
section: "7.2"
order: 2
status: todo
level: senior
notion_id: 3ea3310486798110b06cf7789dc442f4
tags: [domain/frontend, stage/7, level/senior, topic/browser, topic/reflow, topic/repaint, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Reflow и Repaint

↑ [[FE 7.2 Рендеринг и производительность|7.2 Рендеринг и производительность]] · ← [[FE 7.2.1 Critical Rendering Path — DOM, CSSOM, Layout, Paint, Composite|Предыдущая]] · → [[FE 7.2.3 Core Web Vitals — LCP, INP, CLS|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Проверяют, знаете ли вы, какие операции дорогие и как писать плавные анимации.

## Различия

- **Reflow (layout)**: пересчёт геометрии. Дорого, может затрагивать всё дерево.
- **Repaint**: перерисовка без изменения геометрии (цвет, фон).
- **Composite**: только слои (`transform`, `opacity`) — дешевле всего.

## Что вызывает reflow

Изменение `width`, `height`, `margin`, `padding`, `font-size`, добавление и удаление узлов, изменение размера окна. Также **чтение** геометрии после записи: `offsetWidth`, `getBoundingClientRect()`, `scrollTop`.

## Layout thrashing

```ts
// плохо: чтение и запись чередуются, каждый шаг = принудительный layout
items.forEach(el => { el.style.width = el.parentElement!.offsetWidth + 'px' })

// хорошо: сначала все чтения, потом все записи
const widths = items.map(el => el.parentElement!.offsetWidth)
items.forEach((el, i) => { el.style.width = widths[i] + 'px' })
```

## Как уменьшить

- анимировать `transform` и `opacity`, а не `left/top/width`;
- `will-change: transform` точечно (создаёт слой, но тратит память);
- `contain: layout paint` и `content-visibility: auto` для больших блоков;
- изменения пачкой: `DocumentFragment`, классы вместо серии стилей;
- зарезервировать размеры (`width/height`, `aspect-ratio`) для предотвращения CLS.

## Вопросы с ответами

> [!question]- Почему анимировать left плохо, а transform хорошо?
> `left` вызывает layout и paint на каждом кадре, `transform` обрабатывается на композиторе (GPU) без пересчёта макета.

> [!question]- Что такое layout thrashing?
> Чередование чтения и записи геометрии, при котором браузер вынужден пересчитывать layout синхронно на каждой итерации.
