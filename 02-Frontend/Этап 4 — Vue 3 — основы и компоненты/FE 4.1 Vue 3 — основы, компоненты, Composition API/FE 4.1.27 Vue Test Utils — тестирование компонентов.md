---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 27
status: todo
level: middle
notion_id: 3ea3310486798105ad2acf2a9215b3fb
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/testing, topic/vue-test-utils, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Vue Test Utils: тестирование компонентов

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.26 Отличия Vue 2 и Vue 3|Предыдущая]] · → [[FE 4.1.28 Testing Library для Vue — тесты с позиции пользователя|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Практика тестирования компонентов: монтирование, props, события, слоты и изоляция.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Vue Test Utils (VTU)** — официальная библиотека для монтирования компонентов в тестах (с Vitest).

```ts
import { mount, shallowMount, flushPromises } from "@vue/test-utils";
import { describe, it, expect, vi } from "vitest";
import OrderCard from "./OrderCard.vue";

describe("OrderCard", () => {
  const factory = (props = {}) => mount(OrderCard, {
    props: { order: { id: 1, number: "A-1", total: 100 }, ...props },
    global: { plugins: [pinia, router], stubs: { RouterLink: true }, provide: { [ThemeKey as symbol]: theme } },
    slots: { footer: "<em>подвал</em>" },
  });

  it("отображает номер и сумму", () => {
    const w = factory();
    expect(w.text()).toContain("A-1");
    expect(w.find("[data-test=total]").text()).toBe("100,00 ₽");
  });

  it("эмитит save при клике", async () => {
    const w = factory();
    await w.get("button").trigger("click");                    // trigger возвращает nextTick
    expect(w.emitted("save")).toHaveLength(1);
    expect(w.emitted("save")![0]).toEqual([{ id: 1 }]);
  });

  it("обновляется при смене props", async () => {
    const w = factory();
    await w.setProps({ order: { id: 1, number: "B-2", total: 5 } });
    expect(w.text()).toContain("B-2");
  });

  it("v-model на input", async () => {
    const w = factory();
    await w.get("input").setValue("abc");
    expect(w.emitted("update:modelValue")![0]).toEqual(["abc"]);
  });
});
```

| API | Назначение |
|---|---|
| `mount` | полный рендер с дочерними компонентами |
| `shallowMount` | дочерние компоненты заменены заглушками |
| `find/get/findAll/findComponent` | поиск элементов/компонентов (`get` бросает ошибку при отсутствии) |
| `trigger`, `setValue`, `setProps` | взаимодействие |
| `emitted()` | записанные события |
| `wrapper.vm` | экземпляр (лучше не использовать) |
| `global.*` | плагины, stubs, mocks, provide, directives |
| `flushPromises` | дождаться промисов |
| `attachTo: document.body` | монтирование в реальный DOM (фокус, layout) |

Что тестировать: публичный интерфейс — props → отображение, действия пользователя → emits/побочные эффекты, слоты. Не тестируйте внутреннее состояние и приватные методы.

Стабильные селекторы: `data-test`/`data-testid` атрибуты.

## Нюансы и подводные камни

- Не забывайте `await` после `trigger/setValue/setProps`.
- `shallowMount` скрывает интеграцию — используйте осознанно.
- `wrapper.vm.x` завязывает тест на реализацию.
- Асинхронные компоненты/Suspense требуют `flushPromises`/обёртки.
- Проверка структуры DOM через снапшоты — хрупкая.

## Практика

1. Покройте компонент таблицы тестами: рендер, сортировка, события, слоты.
2. Подключите Pinia и Router через `global.plugins`.
3. Замените `wrapper.vm` на проверки через DOM и emits.

## Вопросы с ответами

> [!question]- `mount` или `shallowMount`?
> `mount` рендерит дерево целиком (ближе к реальности), `shallowMount` подменяет дочерние компоненты заглушками для изоляции.

> [!question]- Что тестировать в компоненте?
> Наблюдаемое поведение: рендер по props, реакция на действия, события и слоты.

## Связанные темы

- [[N:3ea33104867981ac9e4cf9d69605a89d]]
- [[N:3ea3310486798103be1ff9a1db673c18]]
