---
type: section
domain: backend
stage: 7
section: "7.6"
order: 6
status: todo
level: senior
notion_id: 3ea3310486798160801dd500d3b45efd
tags: [domain/backend, stage/7, kind/section]
---

# 7.6 DevOps для бэкенд-разработчика: деплой наших систем и CI/CD

↑ [[BE Этап 7 · Middle+ — производительность, observability, надёжность, безопасность|Этап 7]]

Всё, что бэкендеру нужно знать о доставке кода до прода: образы, compose, конфигурация, CI/CD, миграции и откаты. Примеры обобщены; глубокая теория в разделе DevOps.

## Темы
<!-- toc:start -->
**Итого:** 9 тем · ~33 мин · готово 0 из 9

<div class="bar"><span style="width:0%"></span></div>

| # | Тема | Приоритет | Чтение | Статус |
|---|---|---|---|---|
| 1 | [[BE 7.6.1 Путь кода до прода — сборка, образ, registry, миграции, деплой\|Путь кода до прода: сборка, образ, registry, миграции, деплой]] | <span class="badge nice">По желанию</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 2 | [[BE 7.6.2 Dockerfile для .NET-микросервисов — общий core-образ, multi-stage, как у нас\|Dockerfile для .NET-микросервисов: общий core-образ, multi-stage, как у нас]] | <span class="badge nice">По желанию</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 3 | [[BE 7.6.3 Как поднимается Clinic — docker compose, Makefile, порядок запуска, healthcheck\|Как поднимается Clinic: docker compose, Makefile, порядок запуска, healthcheck]] | <span class="badge nice">По желанию</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 4 | [[BE 7.6.4 Конфигурация и секреты — env-файлы, Ansible-фабрика, окружения dev-staging-prod\|Конфигурация и секреты: env-файлы, Ansible-фабрика, окружения dev∕staging∕prod]] | <span class="badge nice">По желанию</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 5 | [[BE 7.6.5 CI-CD для .NET-микросервисов и фронта в GitLab — пайплайн от MR до прода\|CI∕CD для .NET-микросервисов и фронта в GitLab: пайплайн от MR до прода]] | <span class="badge nice">По желанию</span> | 5 мин | <span class="badge todo">Не начато</span> |
| 6 | [[BE 7.6.6 Миграции БД при деплое — Flyway, goose, EF и обратная совместимость\|Миграции БД при деплое: Flyway, goose, EF и обратная совместимость]] | <span class="badge nice">По желанию</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 7 | [[BE 7.6.7 Готовность сервиса к эксплуатации — health checks, graceful shutdown, логи, метрики\|Готовность сервиса к эксплуатации: health checks, graceful shutdown, логи, метрики]] | <span class="badge nice">По желанию</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 8 | [[BE 7.6.8 Выкладка, откат и разбор инцидентов глазами бэкендера\|Выкладка, откат и разбор инцидентов глазами бэкендера]] | <span class="badge nice">По желанию</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 9 | [[BE 7.6.9 Aspire — оркестрация локальной разработки и деплой\|Aspire: оркестрация локальной разработки и деплой]] | <span class="badge should">Желательно</span> | 7 мин | <span class="badge todo">Не начато</span> |
<!-- toc:end -->

## Чек-лист раздела
- [ ] Прочитал все темы
- [ ] Могу объяснить каждую тему за 2 минуты вслух
