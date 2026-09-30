---
type: topic
domain: backend
stage: 6
section: "6.2"
order: 5
status: todo
level: junior
notion_id: 3ea33104867981eab321da100aae4744
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/nestjs, topic/aspnet, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# NestJS и ASP.NET Core: сравнение концепций

↑ [[BE 6.2 NestJS|6.2 NestJS]] · ← [[BE 6.2.4 Конфигурация, аутентификация (Passport, JWT), Swagger|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->


































> [!info] Зачем это на собесе
> Для C#-разработчика: показывает, что вы быстро переносите знания между стеками.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Концепция | NestJS | ASP.NET Core |
|---|---|---|
| Точка входа | `main.ts` (`NestFactory.create`) | `Program.cs` |
| Модульность | `@Module` | extension-методы `AddXxx`, сборки |
| DI | встроенный контейнер, scope Default/Request/Transient | встроенный, Singleton/Scoped/Transient |
| Контроллеры | `@Controller`, `@Get` | `[ApiController]`, `[HttpGet]` / Minimal API |
| Валидация | `class-validator` + `ValidationPipe` | DataAnnotations / FluentValidation |
| Middleware | `NestMiddleware` | middleware |
| Фильтры | guards, interceptors, exception filters | filters, `IExceptionHandler` |
| Конфигурация | `@nestjs/config`, env | `IConfiguration`, Options |
| ORM | TypeORM, Prisma, Sequelize, MikroORM | EF Core, Dapper |
| Тесты | Jest, `Test.createTestingModule`, supertest | xUnit, `WebApplicationFactory` |
| Документация | `@nestjs/swagger` | OpenAPI (`AddOpenApi`) |
| Фоновые задачи | `@nestjs/schedule`, BullMQ | `BackgroundService`, Hangfire |
| Микросервисы | `@nestjs/microservices` (транспорты) | gRPC, MassTransit |

Различия по существу:

- **Модель исполнения**: Node.js — один поток и event loop (CPU-задачи блокируют); .NET — многопоточность и пул потоков.
- **Типы**: TypeScript стирается во время выполнения — валидация входа обязательна; в C# типы сохраняются.
- **Экосистема**: npm богаче, но нестабильнее по версиям; NuGet более консервативен.
- **Производительность CPU-bound**: .NET существенно быстрее; для I/O-bound разница мала.

## Нюансы и подводные камни

- Не переносите привычки напрямую: в Node.js избегайте блокирующих операций, в .NET — `.Result`.
- Runtime-валидация обязательна в обоих стеках, но в Nest — особенно (нет системы типов в рантайме).
- Управление транзакциями и жизненным циклом соединений устроено по-разному в ORM.

## Практика

1. Реализуйте один и тот же CRUD на Nest и ASP.NET Core, сравните объём кода и время ответа.
2. Составьте свою таблицу соответствий для проекта.

## Вопросы с ответами

> [!question]- Что общего у Nest и ASP.NET Core?
> Модульность, DI, контроллеры с декораторами/атрибутами, конвейер обработки запросов и конфигурация через окружение.

> [!question]- Главное отличие?
> Модель исполнения (event loop против пула потоков) и наличие типов в рантайме.

## Связанные темы

- [[N:3ea331048679814ba0c1f776ed6aad25]]
- [[N:3ea33104867981d283b7e44ebc2a421e]]
