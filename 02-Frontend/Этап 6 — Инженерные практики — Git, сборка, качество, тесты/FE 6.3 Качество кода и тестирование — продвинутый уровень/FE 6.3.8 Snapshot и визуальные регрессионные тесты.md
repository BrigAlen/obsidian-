---
type: topic
domain: frontend
stage: 6
section: "6.3"
order: 8
status: todo
level: middle
notion_id: 3ea331048679814389deeacc696e8f27
tags: [domain/frontend, stage/6, level/middle, topic/snapshot, topic/visual-regression, topic/storybook, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Snapshot и визуальные регрессионные тесты

↑ [[FE 6.3 Качество кода и тестирование — продвинутый уровень|6.3 Качество кода и тестирование: продвинутый уровень]] · ← [[FE 6.3.7 E2E-тесты — Playwright и Cypress|Предыдущая]] · → [[FE 6.3.9 Тестирование доступности — axe|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Snapshot-тесты легко превратить в шум; важно знать, когда они полезны, а когда вредны.

## Snapshot-тесты (структура)

```ts
expect(formatInvoice(data)).toMatchSnapshot()
expect(user).toMatchInlineSnapshot(`{ "id": 1, "name": "Анна" }`)
```

Хороши для стабильных сериализуемых результатов: конфигурации, ответы форматтеров, AST. Плохи для больших DOM-деревьев: разработчики слепо обновляют `-u`.

Правила: маленькие и осмысленные снимки, ревью изменений снимков как кода, предпочитать явные `expect` для важных свойств.

## Визуальные регрессионные тесты

Сравнивают **пиксели** скриншотов с эталоном.

```ts
await expect(page).toHaveScreenshot('dashboard.png', { maxDiffPixelRatio: 0.01 })
```

Инструменты: Playwright `toHaveScreenshot`, Storybook + Chromatic, Percy, Loki.

## Стабильность скриншотов

- фиксированный viewport, шрифты, локаль, часовой пояс;
- отключить анимации и мокать даты;
- эталоны генерировать в том же окружении, что и CI (Docker-образ Playwright);
- скрывать динамические области (`mask`).

## Когда использовать

Дизайн-система и библиотека компонентов — да. Обычные страницы с динамикой — осторожно.

## Вопросы с ответами

> [!question]- Чем плохи snapshot-тесты?
> Большие снимки не показывают намерение и обновляются механически. Изменение приходит и утверждается без анализа.

> [!question]- Как сделать визуальные тесты стабильными?
> Единое окружение (Docker), фиксированные шрифты и viewport, отключённые анимации, мок данных, маски на динамические блоки.
