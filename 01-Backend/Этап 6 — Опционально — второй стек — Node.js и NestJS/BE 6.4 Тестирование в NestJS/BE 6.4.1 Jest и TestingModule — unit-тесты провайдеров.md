---
type: topic
domain: backend
stage: 6
section: "6.4"
order: 1
status: todo
level: junior
notion_id: 3ea331048679817b80e2dffe451eba9f
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/nestjs, topic/testing, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Jest и TestingModule: unit-тесты провайдеров

↑ [[BE 6.4 Тестирование в NestJS|6.4 Тестирование в NestJS]] · → [[BE 6.4.2 E2E-тесты NestJS с supertest|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Как в Nest подменяют зависимости в тестах — аналог DI-подмены в .NET.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`Test.createTestingModule` собирает облегчённый модуль с нужными провайдерами и позволяет заменить зависимости.

```ts
describe("OrdersService", () => {
  let service: OrdersService;
  const repo = { findById: jest.fn(), save: jest.fn() };

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({
      providers: [OrdersService, { provide: OrdersRepository, useValue: repo }],
    }).compile();
    service = moduleRef.get(OrdersService);
    jest.resetAllMocks();
  });

  it("бросает NotFound для неизвестного заказа", async () => {
    repo.findById.mockResolvedValue(null);
    await expect(service.find("42")).rejects.toBeInstanceOf(NotFoundException);
  });

  it("сохраняет заказ", async () => {
    repo.save.mockResolvedValue({ id: "1" });
    await service.create({ customer: "A", quantity: 1 });
    expect(repo.save).toHaveBeenCalledWith(expect.objectContaining({ customer: "A" }));
  });
});
```

Полезные приёмы:

- `overrideProvider(X).useValue(mock)`, `useMocker` для автоматических моков.
- `jest.useFakeTimers()` для времени; `jest.spyOn` для частичных подмен.
- Табличные тесты: `it.each([...])`.
- Vitest — быстрая альтернатива Jest с совместимым API.

## Нюансы и подводные камни

- Тестируйте поведение, а не вызовы моков.
- Не забывайте `await` перед `expect(...).rejects`.
- Общие моки между тестами без сброса дают зависимые тесты.
- Проверяйте типы: моки `useValue` не проверяются компилятором на соответствие интерфейсу.

## Практика

1. Напишите unit-тесты сервиса заказов с заменой репозитория.
2. Используйте `it.each` для набора граничных случаев.
3. Протестируйте код со временем через fake timers.

## Вопросы с ответами

> [!question]- Как подменить зависимость в Nest-тесте?
> Указать альтернативный провайдер в `createTestingModule` или `overrideProvider`.

> [!question]- Jest или Vitest?
> Совместимый API; Vitest быстрее и лучше работает с ESM/TypeScript.

## Связанные темы

- [[N:3ea331048679814ba3a1f8951924e9a4]]
- [[N:3ea33104867981a6941fe8fc0adb0d11]]
