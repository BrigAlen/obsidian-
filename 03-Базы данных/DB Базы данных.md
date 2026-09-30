---
cssclasses: [i-db]
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
<!-- toc:start -->
**Итого:** 62 тем · ~5 ч 41 мин · готово 0 из 62

<div class="bar"><span style="width:0%"></span></div>

| Этап | Приоритет | Чтение | Прогресс |
|---|---|---|---|
| [[DB Этап 1 · Фундамент — реляционная модель и SQL\|Этап 1 · Фундамент: реляционная модель и SQL]] | <span class="badge must">Обязательно</span> | 40 мин | 0 из 11<br><div class="bar"><span style="width:0%"></span></div> |
| [[DB Этап 2 · PostgreSQL глубоко\|Этап 2 · PostgreSQL глубоко]] | <span class="badge must">Обязательно</span> | 39 мин | 0 из 11<br><div class="bar"><span style="width:0%"></span></div> |
| [[DB Этап 3 · ClickHouse и аналитика\|Этап 3 · ClickHouse и аналитика]] | <span class="badge should">Желательно</span> | 40 мин | 0 из 11<br><div class="bar"><span style="width:0%"></span></div> |
| [[DB Этап 4 · Кэш, NoSQL и объектное хранилище — Redis, MongoDB, MinIO\|Этап 4 · Кэш, NoSQL и объектное хранилище: Redis, MongoDB, MinIO]] | <span class="badge should">Желательно</span> | 51 мин | 0 из 12<br><div class="bar"><span style="width:0%"></span></div> |
| [[DB Этап 5 · Миграции и эволюция схем\|Этап 5 · Миграции и эволюция схем]] | <span class="badge should">Желательно</span> | 25 мин | 0 из 5<br><div class="bar"><span style="width:0%"></span></div> |
| [[DB Этап 6 · Senior — масштабирование, репликация, распределённые данные\|Этап 6 · Senior: масштабирование, репликация, распределённые данные]] | <span class="badge should">Желательно</span> | 26 мин | 0 из 6<br><div class="bar"><span style="width:0%"></span></div> |
| [[DB Этап 7 · Эксплуатация и безопасность БД\|Этап 7 · Эксплуатация и безопасность БД]] | <span class="badge nice">По желанию</span> | 2 ч | 0 из 6<br><div class="bar"><span style="width:0%"></span></div> |
<!-- toc:end -->

## Прогресс
```dataview
TABLE WITHOUT ID stage AS Этап, length(rows) AS Всего, length(filter(rows, (r) => r.status = "done")) AS Готово
FROM "03-Базы данных"
WHERE type = "topic"
GROUP BY stage
SORT stage ASC
```
