---
type: topic
domain: frontend
stage: 8
section: "8.2"
order: 12
status: todo
level: senior
notion_id: c070b4691d4845169cbfada7c1277b39
tags: [domain/frontend, stage/8, level/senior, topic/storybook, topic/docs, topic/design-system, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Storybook и документация дизайн-системы

↑ [[FE 8.2 Архитектура фронтенда и паттерны|8.2 Архитектура фронтенда и паттерны]] · ← [[FE 8.2.11 State machines для сложного UI — finite states и XState|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Storybook — стандарт для каталога компонентов и изолированной разработки.

## Что это

Инструмент для разработки и документирования UI-компонентов **в изоляции**, вне приложения. Каждое состояние компонента — «история» (story).

```ts
// Button.stories.ts
import type { Meta, StoryObj } from '@storybook/vue3'
import Button from './Button.vue'

const meta = {
  title: 'UI/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: { variant: { control: 'select', options: ['primary', 'secondary', 'danger'] } },
} satisfies Meta<typeof Button>
export default meta

export const Primary: StoryObj<typeof meta> = { args: { variant: 'primary', label: 'Сохранить' } }
export const Disabled: StoryObj<typeof meta> = { args: { disabled: true, label: 'Сохранить' } }
```

## Возможности

- **Controls**: изменение props в интерфейсе;
- **Autodocs**: документация из типов и JSDoc;
- **Actions**: события компонента;
- **Interaction tests** (`play`-функции, Testing Library);
- **a11y addon** (axe);
- **Viewport, темы**, локализация;
- **Visual tests**: Chromatic, Playwright.

```ts
export const Filled: StoryObj = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    await userEvent.type(canvas.getByLabelText('Email'), 'a@b.c')
    await expect(canvas.getByRole('button')).toBeEnabled()
  },
}
```

## Практика

- истории для всех состояний: default, loading, error, empty, disabled, длинный текст, RTL;
- документация: когда использовать, что не делать, доступность;
- публикация как статический сайт (CI), превью для PR;
- мок API через MSW-аддон;
- версионирование вместе с пакетом дизайн-системы.

## Плюсы и минусы

Плюсы: быстрая разработка, документация как живая спецификация, регрессионные проверки, коммуникация с дизайнерами. Минусы: поддержка историй, дублирование настройки окружения (роутер, Pinia, i18n через decorators).

## Вопросы с ответами

> [!question]- Зачем Storybook, если есть тесты?
> Он даёт визуальный каталог и площадку для дизайнеров и разработчиков, изолированную разработку и основу визуальных и a11y-проверок.

> [!question]- Как подключить Pinia или Router к историям?
> Через глобальные decorators в `.storybook/preview.ts`: регистрация плагинов на экземпляре приложения.
