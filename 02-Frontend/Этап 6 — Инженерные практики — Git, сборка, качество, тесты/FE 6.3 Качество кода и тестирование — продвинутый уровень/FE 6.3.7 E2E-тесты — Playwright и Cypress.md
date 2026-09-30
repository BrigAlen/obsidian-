---
type: topic
domain: frontend
stage: 6
section: "6.3"
order: 7
status: todo
level: middle
notion_id: 3ea3310486798112bc25f11773ddd208
tags: [domain/frontend, stage/6, level/middle, topic/e2e, topic/playwright, topic/cypress, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# E2E-тесты: Playwright и Cypress

↑ [[FE 6.3 Качество кода и тестирование — продвинутый уровень|6.3 Качество кода и тестирование: продвинутый уровень]] · ← [[FE 6.3.6 TDD и написание тестируемого кода|Предыдущая]] · → [[FE 6.3.8 Snapshot и визуальные регрессионные тесты|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->











> [!info] Зачем это на собесе
> E2E проверяет критические пути; спрашивают про flaky-тесты, изоляцию данных и выбор инструмента.

## Playwright

```ts
import { test, expect } from '@playwright/test'

test('пользователь создаёт заказ', async ({ page }) => {
  await page.goto('/orders')
  await page.getByRole('button', { name: 'Новый заказ' }).click()
  await page.getByLabel('Клиент').fill('ООО Ромашка')
  await page.getByRole('button', { name: 'Сохранить' }).click()
  await expect(page.getByText('Заказ создан')).toBeVisible()
})
```

Особенности: несколько браузеров (Chromium, Firefox, WebKit), авто-ожидание элементов, trace viewer, параллельный запуск, `storageState` для входа один раз.

## Playwright vs Cypress

| | Playwright | Cypress |
|---|---|---|
| Браузеры | Chromium, Firefox, WebKit | Chromium-семейство, Firefox |
| Вкладки и домены | поддерживает | ограничено |
| Параллельность | из коробки | платная в облаке или плагины |
| Отладка | trace viewer | time travel в runner |
| Язык | TS/JS, также Python, .NET, Java | JS/TS |

## Против flaky-тестов

- полагаться на авто-ожидание, а не на `sleep`;
- локаторы по роли и `data-testid`;
- тестовые данные создавать через API, а не через UI;
- независимость тестов: каждый сам готовит и убирает данные;
- сеть: мокать сторонние сервисы через `page.route`;
- повторы (`retries: 2`) только в CI, и анализ причин.

## Что покрывать

Критические пути: вход, оформление, платёж, главные CRUD-сценарии. Не пытаться покрыть всё E2E.

## Вопросы с ответами

> [!question]- Почему E2E-тесты нестабильны и как это лечить?
> Гонки с асинхронностью, общие данные, реальная сеть. Лечится авто-ожиданием, изоляцией данных, моками внешних сервисов и разбором причин, а не слепыми retries.

> [!question]- Зачем нужен storageState?
> Сохраняет сессию после логина, чтобы не логиниться в каждом тесте, ускоряя набор.
