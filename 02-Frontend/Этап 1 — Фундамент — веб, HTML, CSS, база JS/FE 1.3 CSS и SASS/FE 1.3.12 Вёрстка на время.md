---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 12
status: todo
level: junior
notion_id: 3ea33104867981bc82efc791639f77c8
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/practice, topic/interview, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Вёрстка на время

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.11 SASS-SCSS — переменные, миксины, функции, @use и @forward|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Практическое задание «сверстайте за 30–40 минут»: оценивают структуру, адаптивность и аккуратность.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Алгоритм действий**:

1. **Анализ макета (3–5 мин)**: сетка, повторяющиеся блоки, типографика, цвета, состояния, адаптив.
2. **Структура HTML** семантическими тегами (`header/nav/main/section/footer`), `button` и `a` по смыслу.
3. **Токены** в `:root`: цвета, отступы, радиусы, шрифты.
4. **Reset**: `box-sizing: border-box`, `margin: 0`, `img { max-width: 100%; display: block }`.
5. **Каркас** Grid/Flex; затем компоненты; затем тонкая доводка.
6. **Адаптив** mobile-first, минимум 2 брейкпоинта.
7. **Состояния**: `:hover`, `:focus-visible`, `:disabled`.
8. **Проверка**: DevTools, разные ширины, клавиатура.

Шаблон старта:

```css
:root { --c-primary: #4f46e5; --c-text: #1f2937; --space: 8px; --radius: 8px; }
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; font: 16px/1.5 system-ui, sans-serif; color: var(--c-text); }
img { max-width: 100%; display: block; }
.container { width: min(100% - 32px, 1120px); margin-inline: auto; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: calc(var(--space) * 2); }
```

Типовые задачи: карточки товаров, шапка с бургер-меню, форма с валидацией, модальное окно, аккордеон на `details/summary`, таблица с прокруткой, sticky-элементы, «зебра», центрирование, лендинг.

Проговаривайте решения вслух: почему Grid, а не Flex; как будет работать на мобильных; что сделали бы с большим временем.

## Нюансы и подводные камни

- Сначала структура и адаптив, потом «пиксель-перфект».
- Фиксированные высоты и размеры ломают адаптивность.
- Забыт `viewport` мета-тег и `alt`.
- Использование `!important` и `position: absolute` для всего.
- Отсутствие состояний и фокуса.

## Практика

1. Сверстайте по скриншоту лендинг за 40 минут на таймер.
2. Сделайте бургер-меню на чистом CSS (`:checked`) и на `details`.
3. Повторите три задания, сравнивая время.

## Вопросы с ответами

> [!question]- С чего начать вёрстку макета?
> С анализа сетки и повторяющихся блоков, затем семантическая структура и токены, только после этого — стилизация.

> [!question]- Как показать зрелость на таком задании?
> Семантика, адаптив, состояния и доступность, а также проговаривание решений.

## Связанные темы

- [[N:3ea33104867981afa824fa9aa72c4259]]
- [[N:3ea3310486798101bb32e955dc77616f]]
