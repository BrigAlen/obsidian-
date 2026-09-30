---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 9
status: todo
level: junior
notion_id: 3ea331048679815781bfd3ecdd4a7e2e
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/animation, topic/performance, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Анимации и transitions

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.8 CSS-переменные|Предыдущая]] · → [[FE 1.3.10 Методологии — БЭМ, scoped styles, CSS Modules|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Ждут знания, какие свойства анимировать дёшево (`transform`, `opacity`) и почему.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Transition** — плавный переход между состояниями; **Animation** — сценарий на `@keyframes`.

```css
.btn { transition: transform .2s ease, background-color .2s ease; }
.btn:hover { transform: translateY(-2px); background-color: var(--accent); }

@keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
.badge { animation: pulse 1.5s ease-in-out infinite; }
.fade-in { animation: fade .3s ease both; }   /* both: сохранить начальное/конечное состояние */
```

| Параметр | Значения |
|---|---|
| `transition-property` | какие свойства |
| `transition-duration`, `animation-duration` | длительность |
| `timing-function` | `ease`, `linear`, `ease-in-out`, `cubic-bezier()`, `steps()` |
| `delay`, `iteration-count`, `direction`, `fill-mode` | задержка, повторы, направление, состояние |

**Производительность**: браузер выполняет `transform` и `opacity` на композиторе (GPU) без layout/paint; анимация `width`, `top`, `margin`, `box-shadow` вызывает reflow/repaint и «лаги».

Пайплайн рендера: **Layout → Paint → Composite**. Стремитесь к Composite-only анимациям.

Подсказка `will-change: transform` — точечно и временно. Уважайте `prefers-reduced-motion`.

JS-анимации: Web Animations API (`el.animate()`), `requestAnimationFrame`; библиотеки (GSAP). Во Vue — `<Transition>`/`<TransitionGroup>`.

## Нюансы и подводные камни

- `display: none` нельзя плавно анимировать обычным transition (используйте `opacity` + `visibility` или `@starting-style`/`allow-discrete`).
- `will-change` на всё подряд расходует память.
- Анимации не должны мешать доступности (мигание > 3 раз в секунду опасно).
- Transition срабатывает только при изменении значения между двумя состояниями.

## Практика

1. Сравните анимации `left` и `transform: translateX` в Performance.
2. Сделайте плавное появление модального окна с `opacity`/`transform`.
3. Отключите анимации при `prefers-reduced-motion`.

## Вопросы с ответами

> [!question]- Какие свойства анимировать дёшево?
> `transform` и `opacity`: они не вызывают layout и обрабатываются на GPU.

> [!question]- Чем transition отличается от animation?
> Transition — переход между двумя состояниями по триггеру; animation — многошаговый сценарий на `@keyframes`.

## Связанные темы

- [[N:3ea33104867981f9896cfe61d70bce85]]
- [[N:3ea33104867981389815e50d96d369e7]]
