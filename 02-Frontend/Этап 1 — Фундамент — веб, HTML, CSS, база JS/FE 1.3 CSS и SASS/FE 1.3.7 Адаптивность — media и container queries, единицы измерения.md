---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 7
status: todo
level: junior
notion_id: 3ea331048679810dbe38e6c71614a1d7
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/responsive, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Адаптивность: media и container queries, единицы измерения

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.6 Grid|Предыдущая]] · → [[FE 1.3.8 CSS-переменные|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->
















> [!info] Зачем это на собесе
> Mobile-first, единицы измерения и container queries — типовые вопросы по адаптивной вёрстке.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Обязательный мета-тег: `<meta name="viewport" content="width=device-width, initial-scale=1">`.

**Mobile-first**: базовые стили для маленьких экранов, расширения через `min-width`.

```css
.grid { display: grid; gap: 12px; }
@media (min-width: 768px)  { .grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1200px) { .grid { grid-template-columns: repeat(4, 1fr); } }
@media (prefers-color-scheme: dark)   { :root { --bg: #111; } }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
@media (hover: hover) and (pointer: fine) { .btn:hover { … } }

/* Container queries: компонент реагирует на размер контейнера, а не окна */
.card-wrapper { container-type: inline-size; }
@container (min-width: 400px) { .card { display: grid; grid-template-columns: 120px 1fr; } }
```

| Единица | Относительно |
|---|---|
| `px` | пиксель CSS |
| `rem` | размер шрифта корня (масштабируется настройками пользователя) |
| `em` | размер шрифта элемента/родителя |
| `%` | родитель |
| `vw/vh`, `dvh/svh/lvh` | размер viewport (`dvh` учитывает динамические панели мобильных) |
| `ch` | ширина символа «0» |
| `fr` | доля в grid |

Гибкая типографика: `font-size: clamp(1rem, 2.5vw, 1.5rem)`; `min()`, `max()`, `clamp()` для размеров без media queries.

Адаптивные изображения — `srcset`/`picture` (см. [[N:3ea33104867981408326d7b9cf34d28d]]).

## Нюансы и подводные камни

- `100vh` на мобильных включает область под адресной строкой: используйте `dvh`.
- Отдельные «брейкпоинты под устройства» устаревают — ориентируйтесь на контент.
- Шрифты в `px` ломают масштабирование пользователем: используйте `rem`.
- Проверяйте касание: размер тач-целей от 44×44 px.
- Горизонтальный скролл на мобильных — обычно из-за элемента с фиксированной шириной.

## Практика

1. Сверстайте страницу mobile-first с тремя брейкпоинтами.
2. Замените несколько media queries на `clamp()` и `auto-fit`.
3. Сделайте карточку с container query.

## Вопросы с ответами

> [!question]- Что такое mobile-first?
> Подход, где базовые стили — для мобильных, а более широкие экраны добавляются через `min-width`.

> [!question]- Container query или media query?
> Container query привязан к размеру контейнера — лучше для переиспользуемых компонентов.

> [!question]- rem или em?
> `rem` относится к корню и предсказуем; `em` — к родителю, полезен внутри компонента.

## Связанные темы

- [[N:3ea331048679818a8392d6c5432189d9]]
- [[N:3ea33104867981f9896cfe61d70bce85]]
