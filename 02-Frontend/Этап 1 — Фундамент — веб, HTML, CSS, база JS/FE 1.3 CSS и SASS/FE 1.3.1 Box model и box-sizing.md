---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 1
status: todo
level: junior
notion_id: 3ea33104867981f28130c63f1c1c9290
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/layout, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Box model и box-sizing

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · → [[FE 1.3.2 Селекторы, псевдоклассы и псевдоэлементы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Самый базовый вопрос по CSS: из чего состоит блок и почему ширина «не совпадает».

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Каждый элемент — прямоугольник: **content → padding → border → margin**.

| Свойство | Что задаёт |
|---|---|
| `width/height` | размер content-области (при `content-box`) |
| `padding` | отступ внутри, фон распространяется |
| `border` | рамка |
| `margin` | отступ снаружи, прозрачный |

`box-sizing`:

| Значение | Ширина элемента |
|---|---|
| `content-box` (по умолчанию) | `width` + padding + border |
| `border-box` | `width` включает padding и border |

```css
*, *::before, *::after { box-sizing: border-box; }   /* привычный сброс */
.card { width: 300px; padding: 16px; border: 1px solid #ddd; }   /* итого 300px при border-box */
```

Типы блоков: `display: block` (на всю строку, принимает размеры), `inline` (в строке, игнорирует `width/height` и вертикальные margin), `inline-block`, `none`, `flex`, `grid`.

**Схлопывание margin**: вертикальные margin соседних блоков (и родителя с первым/последним потомком) объединяются в больший. Не схлопываются в flex/grid и при `overflow` не `visible`, `padding`/`border` у родителя.

## Нюансы и подводные камни

- `margin: auto` центрирует блок с заданной шириной по горизонтали.
- `padding` в процентах считается от ширины родителя (даже сверху и снизу).
- Отрицательные margin допустимы, но усложняют вёрстку.
- `inline`-элементы имеют «пробел» между собой из-за пробельных символов.
- `outline` не влияет на размеры, в отличие от `border`.

## Практика

1. Сравните размеры блока с `content-box` и `border-box` в DevTools.
2. Воспроизведите схлопывание margin и устраните его.
3. Сверстайте карточку с фиксированной шириной и отступами без переполнения.

## Вопросы с ответами

> [!question]- Чем border-box отличается от content-box?
> В `border-box` заданная ширина включает padding и border.

> [!question]- Что такое margin collapsing?
> Вертикальные внешние отступы соседних блоков объединяются в один, равный большему.

## Связанные темы

- [[N:3ea331048679811cb0cbccea1d34e59c]]
- [[N:3ea33104867981539d07fe1eba47e407]]
