---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 28
status: todo
level: middle
notion_id: 3ea3310486798103be1ff9a1db673c18
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/testing, topic/testing-library, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Testing Library для Vue: тесты с позиции пользователя

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.27 Vue Test Utils — тестирование компонентов|Предыдущая]] · → [[FE 4.1.29 Задачи на Vue — написать компонент или composable|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Подход «тестируйте как пользователь»: доступные селекторы и устойчивость к рефакторингу.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**@testing-library/vue** — обёртка над VTU с принципом: тесты должны напоминать то, как пользователь работает с интерфейсом. Ищем элементы по роли, тексту, label — а не по классам и внутренней структуре.

```ts
import { render, screen, within, waitFor } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";

it("добавляет заказ через форму", async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn();
  render(OrderForm, { props: { onSubmit }, global: { plugins: [pinia] } });

  await user.type(screen.getByLabelText("Клиент"), "Иванов");
  await user.selectOptions(screen.getByRole("combobox", { name: "Статус" }), "paid");
  await user.click(screen.getByRole("button", { name: /сохранить/i }));

  expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ customer: "Иванов" }));
  expect(await screen.findByText("Сохранено")).toBeInTheDocument();          // findBy = ожидание появления
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();               // queryBy = отсутствие
});
```

Приоритет запросов (от предпочтительных):

| Запрос | Когда |
|---|---|
| `getByRole(role, { name })` | всё, что имеет роль (кнопки, поля, заголовки): проверяет и доступность |
| `getByLabelText` | поля форм |
| `getByPlaceholderText`, `getByText` | текстовое содержимое |
| `getByDisplayValue`, `getByAltText`, `getByTitle` | специфические случаи |
| `getByTestId` | последнее средство |

Варианты запросов: `getBy` (сразу, бросает при отсутствии), `queryBy` (для проверки отсутствия), `findBy` (асинхронно с ожиданием), `*AllBy`. `waitFor` — повторные проверки; `within(el)` — поиск внутри области. Матчеры `@testing-library/jest-dom`: `toBeInTheDocument`, `toBeVisible`, `toBeDisabled`, `toHaveValue`, `toHaveAccessibleName`.

Плюсы: тесты устойчивы к рефакторингу, побочно проверяют доступность (роли и label); минус — нужны доступные разметка и названия.

## Нюансы и подводные камни

- `userEvent` (реалистичные последовательности событий) предпочтительнее `fireEvent`.
- Не запрашивайте по классам и структуре DOM.
- Не используйте `waitFor` для синхронных проверок.
- Для дат/таймеров — фейковые таймеры и `advanceTimers` в `userEvent.setup`.
- Много `getByTestId` — признак недоступной разметки.

## Практика

1. Перепишите тест формы с VTU на Testing Library.
2. Проверьте доступность через `getByRole` и name.
3. Протестируйте асинхронное появление уведомления через `findBy`.

## Вопросы с ответами

> [!question]- В чём философия Testing Library?
> Тестировать поведение с позиции пользователя, используя доступные селекторы, а не детали реализации.

> [!question]- `getBy`, `queryBy`, `findBy` — разница?
> `getBy` сразу и бросает, `queryBy` возвращает `null` (для отсутствия), `findBy` ждёт появления.

## Связанные темы

- [[N:3ea3310486798105ad2acf2a9215b3fb]]
- [[N:3ea33104867981169f15c64990328a32]]
