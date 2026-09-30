---
type: topic
domain: backend
stage: 4
section: "4.2"
order: 9
status: todo
level: middle
notion_id: 3ea3310486798111a4bafaf4f54018b5
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, topic/performance, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Производительность EF Core и логирование SQL

↑ [[BE 4.2 Entity Framework Core|4.2 Entity Framework Core]] · ← [[BE 4.2.8 Bulk-операции — ExecuteUpdate, ExecuteDelete, батчи|Предыдущая]] · → [[BE 4.2.10 Repository и Unit of Work поверх EF — нужно ли|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> «Запросы EF медленные — что делаете?» Ждут метод: измерить, найти, исправить.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Порядок работы: **измерить → найти узкое место → исправить → проверить**.

### Видимость SQL

```csharp
options.UseNpgsql(cs)
       .LogTo(Console.WriteLine, LogLevel.Information)
       .EnableSensitiveDataLogging()      // только в dev
       .EnableDetailedErrors();
// В запросе
var sql = query.ToQueryString();
```

Дополнительно: `pg_stat_statements`, `EXPLAIN (ANALYZE, BUFFERS)`, OpenTelemetry-трейсинг (`OpenTelemetry.Instrumentation.EntityFrameworkCore`), MiniProfiler.

### Чек-лист

| Проблема | Решение |
|---|---|
| N+1 | Include/проекции |
| Лишние данные | `Select` в DTO |
| Tracking для чтения | `AsNoTracking` |
| Нет индекса | миграция с индексом по фильтру/сортировке |
| Cartesian explosion | `AsSplitQuery` |
| Много мелких запросов | батчинг, кэш |
| Медленная трансляция горячего запроса | compiled query |
| Пул контекстов | `AddDbContextPool` |
| Массовые операции | `ExecuteUpdate`, `COPY` |
| Расхождение планов | `ANALYZE`, статистика |

### Измерение

BenchmarkDotNet для микробенчмарков; нагрузочные тесты (k6, NBomber) для сценариев; метрики: время запроса, число запросов на запрос HTTP, размер ответа.

## Нюансы и подводные камни

- `EnableSensitiveDataLogging` пишет значения параметров — не включайте в проде.
- Оптимизируйте по измерениям, не «по ощущению».
- Разогрев: первый запрос EF медленнее (построение модели, компиляция).
- План запроса зависит от данных; тестируйте на реалистичном объёме.
- Индекс ускоряет чтение и замедляет запись.

## Практика

1. Подключите логирование SQL и подсчитайте запросы для одного эндпоинта.
2. Найдите медленный запрос через `pg_stat_statements` и прочтите `EXPLAIN ANALYZE`.
3. Добавьте индекс и повторите замер.

## Вопросы с ответами

> [!question]- Как найти медленные запросы?
> Логи/трейсинг EF, `pg_stat_statements`, `EXPLAIN ANALYZE`, APM.

> [!question]- Что оптимизировать первым?
> Количество запросов и объём данных (N+1, проекции), затем индексы, потом микро-оптимизации.

## Связанные темы

- [[N:3ea33104867981c48e1fec4912a6ddf3]]
- [[N:3ea33104867981048155ce6c5ea28bef]]
