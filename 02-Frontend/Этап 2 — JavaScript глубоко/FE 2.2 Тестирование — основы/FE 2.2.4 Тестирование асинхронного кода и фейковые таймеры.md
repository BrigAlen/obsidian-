---
type: topic
domain: frontend
stage: 2
section: "2.2"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981978640c558af5eaf71
tags: [domain/frontend, stage/2, level/middle, topic/testing, topic/async, topic/timers, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Тестирование асинхронного кода и фейковые таймеры

↑ [[FE 2.2 Тестирование — основы|2.2 Тестирование: основы]] · ← [[FE 2.2.3 Vitest — основы, моки, spy|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


















> [!info] Зачем это на собесе
> Тесты debounce, поллинга, запросов: как не использовать реальные задержки и не получить flaky-тесты.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Асинхронный тест**: возвращайте промис или используйте `async/await`; иначе тест завершится до проверки.

```ts
it("загружает пользователя", async () => {
  vi.mocked(api.getUser).mockResolvedValue({ id: 1, name: "A" });
  await expect(loadUser(1)).resolves.toMatchObject({ name: "A" });
});

it("бросает при ошибке сети", async () => {
  vi.mocked(api.getUser).mockRejectedValue(new Error("offline"));
  await expect(loadUser(1)).rejects.toThrow("offline");
});
```

**Фейковые таймеры**:

```ts
import { vi, beforeEach, afterEach } from "vitest";
beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

it("debounce вызывает функцию один раз после паузы", () => {
  const fn = vi.fn(); const d = debounce(fn, 300);
  d(); d(); d();
  expect(fn).not.toHaveBeenCalled();
  vi.advanceTimersByTime(300);
  expect(fn).toHaveBeenCalledTimes(1);
});

it("управляет временем и датой", async () => {
  vi.setSystemTime(new Date("2025-01-01T00:00:00Z"));
  expect(new Date().getFullYear()).toBe(2025);
  await vi.advanceTimersByTimeAsync(1000);      // выполняет и микрозадачи промисов
  await vi.runAllTimersAsync();
});
```

Методы: `advanceTimersByTime`, `runAllTimers`, `runOnlyPendingTimers`, `advanceTimersToNextTimer`, `setSystemTime`; асинхронные версии `*Async` нужны, когда таймеры и промисы переплетены.

Ожидание изменения состояния:

```ts
await vi.waitFor(() => expect(spy).toHaveBeenCalled());       // опрос до успеха или таймаута
await flushPromises();                                          // из @vue/test-utils
```

## Нюансы и подводные камни

- Реальные `setTimeout` в тестах замедляют набор и вызывают flaky.
- С фейковыми таймерами промисы не «проматываются»: используйте `await` и `*Async`.
- Забытый `useRealTimers` ломает следующие тесты.
- Не проверяйте порядок микрозадач через `setTimeout(0)`.
- Тест без `await` на асинхронный `expect` даёт ложно-зелёный результат.

## Практика

1. Протестируйте `debounce`, `retry` с backoff и поллинг с фейковыми таймерами.
2. Зафиксируйте текущую дату в тесте форматирования.
3. Найдите тест, забывший `await`, с помощью `expect.assertions`.

## Вопросы с ответами

> [!question]- Как тестировать код с таймерами без ожидания?
> `vi.useFakeTimers()` и ручное продвижение времени через `advanceTimersByTime`.

> [!question]- Почему тест прошёл, хотя проверка ложная?
> Не дождались асинхронный `expect`: тест завершился раньше, чем выполнилась проверка.

## Связанные темы

- [[N:3ea33104867981e9b367fd7cd9d12215]]
- [[N:3ea3310486798159b0ccf7fe498691fa]]
