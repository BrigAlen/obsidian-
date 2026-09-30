---
type: topic
domain: frontend
stage: 6
section: "6.3"
order: 9
status: todo
level: middle
notion_id: 3ea33104867981adac7ee14ae3e3edbb
tags: [domain/frontend, stage/6, level/middle, topic/a11y, topic/axe, topic/testing, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Тестирование доступности: axe

↑ [[FE 6.3 Качество кода и тестирование — продвинутый уровень|6.3 Качество кода и тестирование: продвинутый уровень]] · ← [[FE 6.3.8 Snapshot и визуальные регрессионные тесты|Предыдущая]] · → [[FE 6.3.10 Coverage и тесты в CI|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Доступность — требование закона и качества. Спрашивают, что можно проверить автоматически и что нельзя.

## Что такое axe

`axe-core` — движок проверки доступности. Находит нарушения WCAG в DOM: отсутствие `alt`, низкий контраст, поля без label, неверные ARIA-атрибуты.

## Использование

```ts
// Playwright
import AxeBuilder from '@axe-core/playwright'

test('страница входа доступна', async ({ page }) => {
  await page.goto('/login')
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
  expect(results.violations).toEqual([])
})
```

```ts
// Vitest + компонент
import { axe } from 'vitest-axe'
const { container } = render(Form)
expect(await axe(container)).toHaveNoViolations()
```

Также: `eslint-plugin-vuejs-accessibility`, расширение axe DevTools, Lighthouse.

## Ограничения

Автоматика находит примерно 30–40% проблем. Не ловит:

- осмысленность `alt` и текста ссылок;
- логичный порядок фокуса и работу с клавиатуры;
- корректность озвучки в скринридере.

Нужны ручные проверки: клавиатура (Tab, Enter, Esc), NVDA/VoiceOver, увеличение до 200%.

## Практика

- проверять состояния: модалки, ошибки, раскрытые меню;
- падать в CI на серьёзных нарушениях, остальные — в отчёт;
- использовать семантические теги вместо `div` с ролями.

## Вопросы с ответами

> [!question]- Можно ли полностью проверить доступность автотестами?
> Нет. axe ловит формальные нарушения, но не логику фокуса и осмысленность контента. Нужны ручные проверки клавиатурой и скринридером.
