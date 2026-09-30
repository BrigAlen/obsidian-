---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 2
status: todo
level: junior
notion_id: 3ea33104867981539d07fe1eba47e407
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/selectors, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Селекторы, псевдоклассы и псевдоэлементы

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.1 Box model и box-sizing|Предыдущая]] · → [[FE 1.3.3 Каскад, специфичность, наследование|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

























> [!info] Зачем это на собесе
> Знание селекторов влияет на специфичность и качество CSS; спрашивают `:is`, `:where`, `:has`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Селектор | Пример | Смысл |
|---|---|---|
| Тип, класс, id | `div`, `.card`, `#app` | по тегу, классу, идентификатору |
| Атрибут | `[type="text"]`, `[href^="https"]`, `[data-x~="a"]` | по атрибуту (`^=` начало, `$=` конец, `*=` содержит) |
| Потомок / дочерний | `a b`, `a > b` | любой уровень / прямой потомок |
| Соседи | `a + b`, `a ~ b` | следующий / все следующие |
| Группа | `h1, h2` | несколько |
| Универсальный | `*` | все |

**Псевдоклассы** (состояние):

`:hover`, `:focus`, `:focus-visible`, `:active`, `:disabled`, `:checked`, `:first-child`, `:last-child`, `:nth-child(2n+1)`, `:not(.x)`, `:is(h1, h2)`, `:where()` (нулевая специфичность), `:has(> img)` (родитель по потомку), `:empty`, `:root`, `:valid/:invalid`.

**Псевдоэлементы** (часть элемента): `::before`, `::after` (с `content`), `::first-line`, `::first-letter`, `::placeholder`, `::selection`, `::marker`.

```css
.btn:not(:disabled):hover { background: var(--accent); }
.card:has(img) { display: grid; }
li:nth-child(odd) { background: #f5f5f5; }
.tag::before { content: "#"; opacity: .6; }
```

Синтаксис одним двоеточием — псевдокласс, двумя — псевдоэлемент (`::before`).

## Нюансы и подводные камни

- `:nth-child` считает по всем сиблингам, `:nth-of-type` — по типу.
- `::before/::after` не отображаются без `content` и не для замещаемых элементов (`img`).
- Селектор `:has()` — мощный, но следите за производительностью на больших деревьях.
- Слишком длинные селекторы связывают CSS со структурой DOM.
- `:focus` против `:focus-visible`: последний показывает фокус только при клавиатурной навигации.

## Практика

1. Оформите таблицу «зебра» через `:nth-child`.
2. Реализуйте иконку через `::before` без лишней разметки.
3. Выделите карточки с изображением через `:has()`.

## Вопросы с ответами

> [!question]- Чем псевдокласс отличается от псевдоэлемента?
> Псевдокласс выбирает элемент в определённом состоянии, псевдоэлемент — его часть или генерируемый контент.

> [!question]- Что делает `:where()`?
> Как `:is()`, но с нулевой специфичностью.

## Связанные темы

- [[N:3ea33104867981f28130c63f1c1c9290]]
- [[N:3ea331048679815082f0e88439e55756]]
