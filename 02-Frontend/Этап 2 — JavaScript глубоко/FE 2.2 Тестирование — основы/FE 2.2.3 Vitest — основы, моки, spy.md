---
type: topic
domain: frontend
stage: 2
section: "2.2"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981e9b367fd7cd9d12215
tags: [domain/frontend, stage/2, level/middle, topic/testing, topic/vitest, topic/mocks, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Vitest: основы, моки, spy

↑ [[FE 2.2 Тестирование — основы|2.2 Тестирование: основы]] · ← [[FE 2.2.2 Unit-тесты чистых функций — структура AAA, describe, it, expect|Предыдущая]] · → [[FE 2.2.4 Тестирование асинхронного кода и фейковые таймеры|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Vitest — стандарт для Vite-проектов; спрашивают моки модулей, spy и разницу с Jest.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Vitest — тест-раннер на Vite: те же трансформации, что и в приложении (TS, Vue SFC), быстрый watch/HMR, API совместим с Jest.

```ts
// vitest.config.ts
export default defineConfig({ test: { environment: "jsdom", globals: true, setupFiles: ["./test/setup.ts"], coverage: { provider: "v8" } } });
```

```ts
import { vi, describe, it, expect, beforeEach } from "vitest";

// Mock функции
const cb = vi.fn().mockReturnValue(1);
cb(2); expect(cb).toHaveBeenCalledWith(2); expect(cb).toHaveBeenCalledTimes(1);

// Spy: следим за реальным методом
const spy = vi.spyOn(console, "error").mockImplementation(() => {});

// Мок модуля (hoisted)
vi.mock("./api", () => ({ fetchUser: vi.fn().mockResolvedValue({ id: 1, name: "A" }) }));
import { fetchUser } from "./api";

// Частичный мок
vi.mock("./utils", async (orig) => ({ ...(await orig<typeof import("./utils")>()), nowMs: () => 0 }));

beforeEach(() => { vi.clearAllMocks(); });       // clear: история; reset: + реализации; restore: + spyOn
afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });

vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) }));
```

| Инструмент | Для чего |
|---|---|
| `vi.fn()` | заглушка функции, запись вызовов |
| `vi.spyOn(obj, "m")` | слежение/подмена метода |
| `vi.mock(path, factory)` | замена модуля |
| `vi.stubGlobal/stubEnv` | глобалы и переменные окружения |
| `vi.useFakeTimers()` | таймеры и даты (см. [[N:3ea33104867981978640c558af5eaf71]]) |
| `expectTypeOf` | тесты типов |
| Coverage (v8/istanbul), `--ui`, in-source testing, workspaces | сопутствующие возможности |

Разница с Jest: нативные ESM и TS, `vi` вместо `jest`, hoisting `vi.mock` выполняется аналогично, скорость выше, единый конфиг с Vite.

## Нюансы и подводные камни

- `vi.mock` поднимается вверх файла: нельзя ссылаться на переменные, объявленные в тесте (используйте `vi.hoisted`).
- Не сбрасывать моки между тестами — источник зависимостей между тестами.
- Мок слишком глубоко — тест бесполезен; мокайте границы (сеть, время), а не свои модули.
- `environment: "jsdom"` не полностью эмулирует браузер (нет layout).
- `globals: true` требует типов (`vitest/globals`).

## Практика

1. Настройте Vitest с jsdom, coverage и setup-файлом.
2. Замокайте API-модуль и проверьте, что компонент/функция вызывает его с нужными аргументами.
3. Проверьте вызов `console.error` через spy.

## Вопросы с ответами

> [!question]- Чем `vi.fn` отличается от `vi.spyOn`?
> `fn` создаёт новую заглушку, `spyOn` оборачивает существующий метод, сохраняя возможность вызова оригинала.

> [!question]- Чем Vitest отличается от Jest?
> Работает на Vite (быстро, нативные ESM/TS), совместимый API, единая конфигурация с приложением.

## Связанные темы

- [[N:3ea3310486798185b682cb5226728e69]]
- [[N:3ea33104867981978640c558af5eaf71]]
