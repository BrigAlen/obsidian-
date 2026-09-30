---
type: topic
domain: backend
stage: 4
section: "4.2"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981e88c8ffcdc0440cf35
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, topic/migrations, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Миграции EF Core

↑ [[BE 4.2 Entity Framework Core|4.2 Entity Framework Core]] · ← [[BE 4.2.2 Моделирование — конвенции, Fluent API, связи, owned types, NamingConventions|Предыдущая]] · → [[BE 4.2.4 Change tracking — tracking и AsNoTracking, состояния сущностей|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





















































> [!info] Зачем это на собесе
> Как вы выкатываете изменения схемы в прод без простоя и потерь данных.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Миграция — C#-файл с `Up`/`Down` и snapshot модели. EF сравнивает модель со snapshot и генерирует разницу.

```bash
dotnet ef migrations add AddOrderNumber
dotnet ef migrations script --idempotent -o migrate.sql   # SQL для DBA/CI
dotnet ef database update
dotnet ef migrations remove                               # откат последней неприменённой
```

| Способ применения | Когда |
|---|---|
| `db.Database.MigrateAsync()` при старте | dev, простые сервисы; опасно при нескольких репликах |
| SQL-скрипт (`--idempotent`) в CI/CD | прод |
| Отдельный job/init-контейнер | Kubernetes |
| Migration bundle (`dotnet ef migrations bundle`) | самодостаточный исполняемый файл |

### Безопасные изменения схемы (expand/contract)

1. Добавить новую колонку nullable (совместимо со старым кодом).
2. Выкатить код, пишущий в обе колонки.
3. Мигрировать данные.
4. Переключить чтение, затем удалить старую колонку отдельной миграцией.

## Нюансы и подводные камни

- Переименование колонки EF может сгенерировать как drop+create (потеря данных): проверяйте сгенерированный код.
- Не редактируйте применённые миграции; создавайте новые.
- Конфликты snapshot при параллельной разработке — при merge пересоздавайте миграцию.
- Долгие блокирующие DDL на больших таблицах (создание индекса) — `CREATE INDEX CONCURRENTLY` вручную.
- Автомиграции при старте в нескольких подах → гонка; используйте блокировку или отдельный шаг.

## Практика

1. Сгенерируйте idempotent-скрипт и примените его через psql.
2. Проведите переименование колонки безопасно в 3 шага.
3. Настройте в CI проверку, что модель и миграции синхронны (`dotnet ef migrations has-pending-model-changes`).

## Вопросы с ответами

> [!question]- Как выкатывать миграции в проде?
> Отдельным шагом деплоя: SQL-скрипт или bundle, до/вместе с релизом, с обратной совместимостью кода.

> [!question]- Что опасно в MigrateAsync при старте?
> Гонка между репликами и долгие DDL при запуске приложения.

> [!question]- Как сделать переименование без потери данных?
> `RenameColumn` вручную вместо drop+add или expand/contract.

## Связанные темы

- [[N:3ea33104867981bfbfc4ec436ba6c342]]
- [[N:3ea331048679813da621c1c306b63386]]
