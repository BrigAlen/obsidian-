---
type: topic
domain: backend
stage: 6
section: "6.2"
order: 1
status: todo
level: junior
notion_id: 3ea33104867981c0b1f6cbbaf8a20394
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/nestjs, topic/di, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Архитектура NestJS: модули, провайдеры, DI

↑ [[BE 6.2 NestJS|6.2 NestJS]] · → [[BE 6.2.2 Контроллеры, DTO, ValidationPipe|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->




































> [!info] Зачем это на собесе
> Если в вакансии есть Node.js/NestJS, спросят про модули и DI; знание ASP.NET Core помогает объяснить по аналогии.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

NestJS — фреймворк для серверных приложений на TypeScript поверх Express или Fastify. Архитектура вдохновлена Angular и ASP.NET.

| Понятие | Роль |
|---|---|
| Module (`@Module`) | группирует контроллеры и провайдеры, задаёт границы; `imports`, `providers`, `controllers`, `exports` |
| Provider (`@Injectable`) | сервис, репозиторий, фабрика — то, что внедряется |
| Controller (`@Controller`) | обрабатывает HTTP-запросы |
| Dependency Injection | внедрение через конструктор по токену (обычно класс) |
| Scope | `DEFAULT` (singleton), `REQUEST`, `TRANSIENT` |

```ts
@Injectable()
export class OrdersService {
  constructor(private readonly repo: OrdersRepository, private readonly config: ConfigService) {}
  find(id: string) { return this.repo.findById(id); }
}

@Module({
  imports: [ConfigModule],
  controllers: [OrdersController],
  providers: [OrdersService, OrdersRepository],
  exports: [OrdersService],          // доступен другим модулям
})
export class OrdersModule {}
```

Кастомные провайдеры: `useClass`, `useValue`, `useFactory` (асинхронная фабрика), `useExisting`; токены-строки/символы с `@Inject('TOKEN')`. Динамические модули (`forRoot`, `forRootAsync`) настраиваются при импорте.

## Нюансы и подводные камни

- Провайдер, не экспортированный из модуля, недоступен снаружи.
- Циклические зависимости лечатся `forwardRef`, но чаще указывают на плохую декомпозицию.
- `REQUEST`-scope распространяется вверх по цепочке зависимостей и замедляет приложение.
- Декораторы работают через `reflect-metadata` и требуют `emitDecoratorMetadata`.
- Не создавайте экземпляры вручную (`new Service()`): теряется DI.

## Практика

1. Создайте модуль заказов с сервисом и репозиторием.
2. Подключите провайдер через `useFactory` с асинхронной инициализацией.
3. Напишите динамический модуль с `forRoot`.

## Вопросы с ответами

> [!question]- Как устроен DI в NestJS?
> Провайдеры регистрируются в модулях, контейнер разрешает зависимости по типам/токенам конструктора и управляет временем жизни.

> [!question]- Зачем exports?
> Чтобы сделать провайдер модуля доступным импортирующим модулям.

## Связанные темы

- [[N:3ea331048679815e88ece14f7c6b80ae]]
- [[N:3ea33104867981138808c8ece7b97ae7]]
