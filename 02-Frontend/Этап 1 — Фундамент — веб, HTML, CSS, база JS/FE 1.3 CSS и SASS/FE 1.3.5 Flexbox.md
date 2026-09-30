---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 5
status: todo
level: junior
notion_id: 3ea3310486798174b46ec9e364d8fb92
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/flexbox, topic/layout, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Flexbox

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.4 Позиционирование, z-index, stacking context|Предыдущая]] · → [[FE 1.3.6 Grid|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->














> [!info] Зачем это на собесе
> Flexbox — основной инструмент одномерной раскладки; спрашивают оси, `flex: 1` и центрирование.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Flex-контейнер раскладывает элементы вдоль **главной оси** (`flex-direction`), поперёк — **поперечная ось**.

| Свойство контейнера | Значение |
|---|---|
| `display: flex` | включить |
| `flex-direction` | `row` / `column` / `*-reverse` |
| `justify-content` | по главной оси: `flex-start`, `center`, `space-between`, `space-around`, `space-evenly` |
| `align-items` | по поперечной: `stretch`, `center`, `flex-start`, `baseline` |
| `flex-wrap` | `nowrap` / `wrap` |
| `gap` | промежутки |
| `align-content` | строки при `wrap` |

| Свойство элемента | Значение |
|---|---|
| `flex-grow` | доля свободного места |
| `flex-shrink` | как сжимается при нехватке |
| `flex-basis` | базовый размер |
| `flex: 1` | `1 1 0%` — занять всё свободное место поровну |
| `align-self`, `order` | индивидуальное выравнивание, порядок |

```css
.row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.center { display: flex; place-content: center; min-height: 100vh; }   /* центрирование */
.sidebar { flex: 0 0 240px; }
.content { flex: 1; min-width: 0; }   /* min-width: 0 позволяет сжиматься длинному содержимому */
```

## Нюансы и подводные камни

- У flex-элементов `min-width: auto` — длинный текст/`pre` не сжимается: нужен `min-width: 0` и `overflow`.
- `margin: auto` внутри flex поглощает свободное место (удобно для «оттолкнуть» элемент).
- `flex-basis` приоритетнее `width` в главной оси.
- `gap` поддерживается во flex во всех современных браузерах.
- Для двумерной раскладки используйте Grid.

## Практика

1. Сверстайте шапку: логотип слева, меню по центру, кнопки справа.
2. Сделайте «липкий» футер с `min-height` и `flex: 1`.
3. Воспроизведите и исправьте проблему с длинным текстом в flex-элементе.

## Вопросы с ответами

> [!question]- Что значит `flex: 1`?
> Элемент растёт и сжимается, занимая равную долю свободного места (`1 1 0%`).

> [!question]- Как отцентрировать элемент по обеим осям?
> `display: flex; justify-content: center; align-items: center;` (или `place-content: center`).

## Связанные темы

- [[N:3ea33104867981f98d0ce4cd6ed713a0]]
- [[N:3ea331048679818a8392d6c5432189d9]]
