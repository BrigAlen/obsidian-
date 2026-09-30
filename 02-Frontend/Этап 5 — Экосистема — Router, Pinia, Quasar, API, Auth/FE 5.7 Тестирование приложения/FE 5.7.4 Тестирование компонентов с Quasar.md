---
type: topic
domain: frontend
stage: 5
section: "5.7"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981d68446c879a4fae8c5
tags: [domain/frontend, stage/5, level/middle, topic/testing, topic/quasar, topic/components, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Тестирование компонентов с Quasar

↑ [[FE 5.7 Тестирование приложения|5.7 Тестирование приложения]] · ← [[FE 5.7.3 Тестирование роутера и navigation guards|Предыдущая]] · → [[FE 5.7.5 Тестирование Vue Query и авторизации (мок Keycloak)|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Компоненты Quasar требуют плагина и имеют особенности рендера (порталы, диалоги, меню).

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Официальный пакет **`@quasar/quasar-app-extension-testing-unit-vitest`** (или ручная настройка): плагин Quasar и глобальные настройки в setup-файле.

```ts
// vitest.config.ts
export default defineConfig({ plugins: [vue({ template: { transformAssetUrls } }), quasar({ sassVariables: "src/css/quasar.variables.scss" })],
  test: { environment: "jsdom", globals: true, setupFiles: ["test/setup.ts"], css: false } });

// test/setup.ts
import { installQuasarPlugin } from "@quasar/quasar-app-extension-testing-unit-vitest";
import { Notify, Dialog } from "quasar";
installQuasarPlugin({ plugins: { Notify, Dialog } });        // глобальная установка Quasar для всех тестов
```

```ts
import { mount } from "@vue/test-utils";
import { render, screen } from "@testing-library/vue";

it("QInput показывает ошибку валидации", async () => {
  const user = userEvent.setup();
  render(OrderForm, { global: { plugins: [pinia] } });
  await user.click(screen.getByRole("button", { name: /сохранить/i }));
  expect(await screen.findByText("Обязательное поле")).toBeInTheDocument();
});

it("уведомление вызывается", async () => {
  const notify = vi.spyOn(Notify, "create");                  // проверка вызова плагина
  await mountAndSubmit();
  expect(notify).toHaveBeenCalledWith(expect.objectContaining({ type: "positive" }));
});
```

Особенности:

| Проблема | Решение |
|---|---|
| Порталы: `QDialog`, `QMenu`, `QSelect`-меню рендерятся в `body` | `screen`/`document.body` (Testing Library), `attachTo`, `findComponent` |
| Анимации `Transition` | `global.stubs: { transition: false }` или отключить (`quasar` без анимаций в тестах) |
| `QSelect`: выбор опции | клик по полю → `findByRole("option", ...)` → клик |
| `QTable` серверная пагинация | эмиссия `@request`, проверка вызова API |
| `$q` в компонентах | установленный плагин или `mocks: { $q }`; `useQuasar()` возвращает реальный объект после `installQuasarPlugin` |
| Иконки и шрифты | не нужны (заглушки) |
| `QForm.validate()` | `await form.validate()` внутри `wrapper.vm`/ref, либо через клик submit |
| Размер экрана | `$q.screen` — переопределить в `installQuasarPlugin`/мокнуть |
| Дата/`QDate` | фиксированные значения, фейковое время |

Практика: тесты через доступные роли/подписи, а не классы `.q-*` (они меняются между версиями). Обёртки над Quasar-компонентами (см. [[N:3ea33104867981059bb4e4c24f055d22]]) тестируются как пользовательский интерфейс.

## Нюансы и подводные камни

- Без `installQuasarPlugin` компоненты рендерятся с предупреждениями/ошибками.
- Асинхронное поведение меню и диалогов: `findBy…`/`waitFor`.
- Тесты, завязанные на классы `q-*`, ломаются при обновлении.
- CSS в jsdom не считается: видимость элементов и layout недоступны.
- Тяжёлые компоненты (`QTable` с большим набором данных) замедляют тесты.

## Практика

1. Настройте Vitest с Quasar и напишите тест формы с `QInput/QSelect`.
2. Протестируйте `QDialog` подтверждения удаления.
3. Проверьте вызов `Notify` после успешного сохранения.

## Вопросы с ответами

> [!question]- Как подключить Quasar в тестах?
> Через `installQuasarPlugin` в setup-файле (или `global.plugins: [Quasar]`) с нужными плагинами.

> [!question]- Почему диалог не находится в `wrapper`?
> Он рендерится в `body` через портал: ищите через `screen`/`document.body`.

## Связанные темы

- [[N:3ea33104867981a18b7bf87480a1b51f]]
- [[N:3ea33104867981c0b163f7c428eb6b11]]
