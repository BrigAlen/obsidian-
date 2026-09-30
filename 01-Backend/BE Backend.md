---
type: domain
domain: backend
tags: [backend, moc]
---

# ⚙️ Backend

C#, .NET 9, ASP.NET Core, EF Core, gRPC, GraphQL, Kafka, микросервисы, observability.

↑ [[00 Карта]]

> [!tip] Как проходить
> Этапы по порядку → внутри этапа разделы по порядку. После каждой темы: карточки → квиз → перенос в статус `done`.

## Этапы
- [[BE Этап 1 · Фундамент — сети, ОС, основы C|Этап 1 · Фундамент: сети, ОС, основы C#]]
- [[BE Этап 2 · C глубоко и .NET runtime|Этап 2 · C# глубоко и .NET runtime]]
- [[BE Этап 3 · ASP.NET Core|Этап 3 · ASP.NET Core]]
- [[BE Этап 4 · Данные в .NET — ADO.NET, Dapper, EF Core|Этап 4 · Данные в .NET: ADO.NET, Dapper, EF Core]]
- [[BE Этап 5 · Интеграции — REST, gRPC, GraphQL, Kafka и очереди, внешние API|Этап 5 · Интеграции: REST, gRPC, GraphQL, Kafka и очереди, внешние API]]
- [[BE Этап 6 · Опционально — второй стек — Node.js и NestJS|Этап 6 · Опционально: второй стек — Node.js и NestJS]]
- [[BE Этап 7 · Middle+ — производительность, observability, надёжность, безопасность|Этап 7 · Middle+: производительность, observability, надёжность, безопасность]]
- [[BE Этап 8 · Senior — архитектура, DDD, микросервисы, System Design|Этап 8 · Senior: архитектура, DDD, микросервисы, System Design]]
- [[BE Этап 9 · Техлидство и финальная подготовка|Этап 9 · Техлидство и финальная подготовка]]

## Прогресс
```dataview
TABLE WITHOUT ID stage AS Этап, length(rows) AS Всего, length(filter(rows, (r) => r.status = "done")) AS Готово
FROM "01-Backend"
WHERE type = "topic"
GROUP BY stage
SORT stage ASC
```
