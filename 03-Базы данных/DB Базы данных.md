---
type: domain
domain: db
tags: [domain/db, kind/moc]
---

# Базы данных

SQL, PostgreSQL, ClickHouse, Redis, MongoDB, MinIO (S3), миграции, репликация и шардирование.

↑ [[00 Карта]]

> [!tip] Как проходить
> Этапы по порядку → внутри этапа разделы по порядку. После каждой темы: карточки → квиз → перенос в статус `done`.

## Этапы
- [[DB Этап 1 · Фундамент — реляционная модель и SQL|Этап 1 · Фундамент: реляционная модель и SQL]]
- [[DB Этап 2 · PostgreSQL глубоко|Этап 2 · PostgreSQL глубоко]]
- [[DB Этап 3 · ClickHouse и аналитика|Этап 3 · ClickHouse и аналитика]]
- [[DB Этап 4 · Кэш, NoSQL и объектное хранилище — Redis, MongoDB, MinIO|Этап 4 · Кэш, NoSQL и объектное хранилище: Redis, MongoDB, MinIO]]
- [[DB Этап 5 · Миграции и эволюция схем|Этап 5 · Миграции и эволюция схем]]
- [[DB Этап 6 · Senior — масштабирование, репликация, распределённые данные|Этап 6 · Senior: масштабирование, репликация, распределённые данные]]
- [[DB Этап 7 · Эксплуатация и безопасность БД|Этап 7 · Эксплуатация и безопасность БД]]

## Прогресс
```dataview
TABLE WITHOUT ID stage AS Этап, length(rows) AS Всего, length(filter(rows, (r) => r.status = "done")) AS Готово
FROM "03-Базы данных"
WHERE type = "topic"
GROUP BY stage
SORT stage ASC
```
