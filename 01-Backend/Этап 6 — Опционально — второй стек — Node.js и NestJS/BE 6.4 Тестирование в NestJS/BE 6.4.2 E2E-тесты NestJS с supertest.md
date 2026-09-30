---
type: topic
domain: backend
stage: 6
section: "6.4"
order: 2
status: todo
level: junior
notion_id: 3ea33104867981a6941fe8fc0adb0d11
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/nestjs, topic/testing, topic/e2e, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# E2E-тесты NestJS с supertest

↑ [[BE 6.4 Тестирование в NestJS|6.4 Тестирование в NestJS]] · ← [[BE 6.4.1 Jest и TestingModule — unit-тесты провайдеров|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->














> [!info] Зачем это на собесе
> Аналог `WebApplicationFactory` в Node.js: проверка всего HTTP-конвейера.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

E2E-тест поднимает приложение (без сетевого порта) и отправляет HTTP-запросы через supertest.

```ts
describe("Orders (e2e)", () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({ imports: [AppModule] })
      .overrideProvider(PaymentsGateway).useValue({ charge: jest.fn().mockResolvedValue({ ok: true }) })
      .compile();
    app = moduleRef.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));  // как в main.ts
    await app.init();
  });
  afterAll(() => app.close());

  it("POST /orders создаёт заказ", async () => {
    const res = await request(app.getHttpServer())
      .post("/orders").set("Authorization", `Bearer ${token}`)
      .send({ customer: "A", quantity: 2 }).expect(201);
    expect(res.body).toMatchObject({ customer: "A" });
  });

  it("возвращает 400 при неверных данных", () =>
    request(app.getHttpServer()).post("/orders").send({ quantity: -1 }).expect(400));
});
```

Реальная БД: Testcontainers (`@testcontainers/postgresql`) + миграции; очистка данных между тестами (TRUNCATE в `beforeEach`). Внешние сервисы — nock/MSW/WireMock.

## Нюансы и подводные камни

- Настройки из `main.ts` (pipes, filters, prefix) нужно повторить в тесте, иначе тест проверяет другое приложение.
- Не забывайте закрывать приложение и соединения (`app.close()`), иначе Jest не завершится.
- Тесты не должны зависеть от порядка выполнения.
- Не используйте «одну общую БД» без очистки.

## Практика

1. Напишите e2e для CRUD заказов с реальной БД в контейнере.
2. Проверьте 401/403 для защищённых маршрутов.
3. Выведите общий `setupApp(app)` и используйте в `main.ts` и тестах.

## Вопросы с ответами

> [!question]- Чем e2e отличается от unit в Nest?
> E2E проходит весь HTTP-конвейер (pipes, guards, фильтры) с реальными или подменёнными внешними зависимостями.

> [!question]- Почему тест не завершается?
> Не закрыто приложение или соединения с БД.

## Связанные темы

- [[N:3ea331048679817b80e2dffe451eba9f]]
- [[N:3ea33104867981348f7afd2d924a3214]]
