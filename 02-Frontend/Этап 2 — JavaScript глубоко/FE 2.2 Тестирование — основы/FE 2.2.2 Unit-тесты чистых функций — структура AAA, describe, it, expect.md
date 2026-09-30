---
type: topic
domain: frontend
stage: 2
section: "2.2"
order: 2
status: todo
level: middle
notion_id: 3ea3310486798185b682cb5226728e69
tags: [domain/frontend, stage/2, level/middle, topic/testing, topic/unit, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Unit-тесты чистых функций: структура AAA, describe, it, expect

↑ [[FE 2.2 Тестирование — основы|2.2 Тестирование: основы]] · ← [[FE 2.2.1 Пирамида тестирования|Предыдущая]] · → [[FE 2.2.3 Vitest — основы, моки, spy|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
























> [!info] Зачем это на собесе
> База: как выглядит хороший unit-тест и как его называть.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Чистые функции тестировать проще всего: вход → выход, без моков.

**AAA**: Arrange (подготовка), Act (действие), Assert (проверка).

```ts
import { describe, it, expect } from "vitest";
import { formatPrice, groupBy } from "./utils";

describe("formatPrice", () => {
  it("форматирует рубли с разделителями", () => {
    // Arrange
    const value = 1234.5;
    // Act
    const result = formatPrice(value, "RUB");
    // Assert
    expect(result).toBe("1 234,50 ₽");
  });

  it.each([
    [0, "0,00 ₽"],
    [-5, "−5,00 ₽"],
    [1e6, "1 000 000,00 ₽"],
  ])("formatPrice(%d) → %s", (input, expected) => {
    expect(formatPrice(input, "RUB")).toBe(expected);
  });

  it("бросает ошибку для NaN", () => {
    expect(() => formatPrice(NaN, "RUB")).toThrow(/некорректное/i);
  });
});

describe("groupBy", () => {
  it("группирует по ключу", () => {
    expect(groupBy([{ t: "a" }, { t: "b" }, { t: "a" }], x => x.t)).toEqual({ a: [{ t: "a" }, { t: "a" }], b: [{ t: "b" }] });
  });
});
```

Матчеры: `toBe` (строгое равенство `Object.is`), `toEqual` (структурное), `toStrictEqual`, `toBeTruthy`, `toContain`, `toHaveLength`, `toMatchObject`, `toThrow`, `toBeCloseTo` (числа с плавающей точкой), `resolves/rejects`.

Что тестировать: нормальные значения, границы (0, пусто, максимум), ошибки, специальные значения (`null`, `NaN`, отрицательные), идемпотентность и инварианты.

Название теста читается как требование: «возвращает …, когда …».

## Нюансы и подводные камни

- Один тест — одно поведение.
- `toBe` для объектов сравнивает ссылки: используйте `toEqual`.
- Не дублируйте логику функции в тесте (вычисление ожидаемого тем же кодом).
- Числа с плавающей точкой: `toBeCloseTo`.
- Порядок тестов не должен влиять на результат.

## Практика

1. Покройте набор утилит (форматирование, группировка, валидация) табличными тестами.
2. Проверьте покрытие ветвлений и добавьте пропущенные.
3. Сформулируйте названия тестов как требования.

## Вопросы с ответами

> [!question]- Что такое AAA?
> Структура теста: подготовка данных, вызов, проверка результата.

> [!question]- `toBe` или `toEqual`?
> `toBe` — сравнение по `Object.is`, `toEqual` — глубокое структурное сравнение.

## Связанные темы

- [[N:3ea3310486798198b292ca6f533bfc9f]]
- [[N:3ea33104867981e9b367fd7cd9d12215]]
