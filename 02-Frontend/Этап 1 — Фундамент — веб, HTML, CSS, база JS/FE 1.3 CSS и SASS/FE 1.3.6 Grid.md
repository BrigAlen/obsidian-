---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 6
status: todo
level: junior
notion_id: 3ea331048679818a8392d6c5432189d9
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/grid, topic/layout, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Grid

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.5 Flexbox|Предыдущая]] · → [[FE 1.3.7 Адаптивность — media и container queries, единицы измерения|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Grid — двумерная раскладка; спрашивают `fr`, `minmax`, `auto-fit`, `grid-template-areas`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```css
.layout {
  display: grid;
  grid-template-columns: 240px 1fr;            /* сайдбар + гибкая колонка */
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  gap: 16px;
  min-height: 100vh;
}
.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }

/* Адаптивная сетка карточек без media queries */
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }
```

| Понятие | Смысл |
|---|---|
| `fr` | доля свободного пространства |
| `minmax(min, max)` | диапазон размера трека |
| `repeat(n, …)` / `auto-fill` / `auto-fit` | повторение; `auto-fit` схлопывает пустые треки |
| `grid-auto-flow`, `grid-auto-rows` | неявные треки |
| `grid-column: 1 / span 2` | размещение по линиям |
| `place-items`, `justify-*`, `align-*` | выравнивание |
| `subgrid` | вложенная сетка использует треки родителя |
| `dense` | заполнение пропусков |

Flexbox vs Grid: flex — одна ось (ряд или колонка), контент определяет размеры; grid — две оси, макет определяет размеры. Часто вместе: grid для каркаса страницы, flex внутри компонентов.

## Нюансы и подводные камни

- `1fr` имеет минимум `auto`: длинное содержимое расширяет колонку — используйте `minmax(0, 1fr)`.
- Разница `auto-fill` и `auto-fit` проявляется, когда элементов меньше, чем помещается.
- Неявные строки создаются автоматически: задавайте `grid-auto-rows`.
- Grid не заменяет таблицу для табличных данных.

## Практика

1. Сверстайте каркас страницы через `grid-template-areas` и перестройте на мобильных.
2. Сделайте галерею с `auto-fill/minmax`.
3. Используйте `subgrid` для выравнивания заголовков карточек.

## Вопросы с ответами

> [!question]- Grid или Flexbox?
> Grid — для двумерной раскладки, Flexbox — для одномерных рядов и выравнивания.

> [!question]- Что делает `minmax(240px, 1fr)`?
> Колонка не уже 240px и растягивается до доли свободного места.

## Связанные темы

- [[N:3ea3310486798174b46ec9e364d8fb92]]
- [[N:3ea331048679810dbe38e6c71614a1d7]]
