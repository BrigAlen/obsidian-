---
type: topic
domain: frontend
stage: 8
section: "8.2"
order: 11
status: todo
level: senior
notion_id: 9f43dd24dec0474686188202c28d2df5
tags: [domain/frontend, stage/8, level/senior, topic/xstate, topic/state-machine, topic/ui, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# State machines для сложного UI: finite states и XState

↑ [[FE 8.2 Архитектура фронтенда и паттерны|8.2 Архитектура фронтенда и паттерны]] · ← [[FE 8.2.10 Тестируемая архитектура и стратегия тестирования проекта|Предыдущая]] · → [[FE 8.2.12 Storybook и документация дизайн-системы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Показывает умение моделировать сложные сценарии (формы, мастеры, загрузка) без комбинаторики булевых флагов.

## Проблема булевых флагов

```ts
const isLoading = ref(false), isError = ref(false), isSuccess = ref(false)
// возможны невозможные состояния: isLoading && isSuccess
```

## Конечный автомат

Состояний конечное число; в каждый момент активно **одно**; переходы происходят по событиям; недопустимые переходы игнорируются.

```ts
import { createMachine, assign } from 'xstate'

export const fetchMachine = createMachine({
  id: 'fetch',
  initial: 'idle',
  context: { data: null as Data | null, error: null as string | null, retries: 0 },
  states: {
    idle: { on: { FETCH: 'loading' } },
    loading: {
      invoke: {
        src: 'load',
        onDone: { target: 'success', actions: assign({ data: ({ event }) => event.output }) },
        onError: { target: 'failure', actions: assign({ error: ({ event }) => String(event.error) }) },
      },
    },
    success: { on: { FETCH: 'loading' } },
    failure: { on: { RETRY: { target: 'loading', guard: ({ context }) => context.retries < 3 } } },
  },
})
```

## Понятия XState

- **состояния**, **события**, **переходы**;
- **context** — расширенное данные;
- **guards** — условия переходов;
- **actions** — побочные эффекты при переходе;
- **invoke / actors** — асинхронные задачи;
- иерархические и параллельные состояния;
- **statechart** — расширенная модель Харела.

## Применение во Vue

```ts
import { useMachine } from '@xstate/vue'
const { snapshot, send } = useMachine(fetchMachine)
// snapshot.value.matches('loading'), send({ type: 'FETCH' })
```

## Где полезно

Многошаговые формы (мастера), оплата, загрузка файлов с прогрессом, аутентификация, редакторы, drag-and-drop. Визуализатор (Stately) и модель для тестирования.

## Когда избыточно

Простые переключатели и простая загрузка. Для небольших задач достаточно `status: 'idle' | 'loading' | 'success' | 'error'` — минимальная «машина» на union-типе.

## Вопросы с ответами

> [!question]- Чем машина состояний лучше набора булевых флагов?
> Исключает невозможные комбинации, делает переходы явными, поддаётся визуализации и тестированию.

> [!question]- Как смоделировать «мастер из трёх шагов»?
> Состояния `step1`, `step2`, `step3`, `submitting`, `done`; события `NEXT`, `BACK`, `SUBMIT`; guards по валидности шага.
