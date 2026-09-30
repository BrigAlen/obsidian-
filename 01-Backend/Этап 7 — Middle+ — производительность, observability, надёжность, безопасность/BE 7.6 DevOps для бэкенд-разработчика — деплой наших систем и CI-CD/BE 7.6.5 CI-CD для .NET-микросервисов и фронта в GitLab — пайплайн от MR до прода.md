---
type: topic
domain: backend
stage: 7
section: "7.6"
order: 5
status: todo
level: senior
notion_id: 3ea33104867981e1abd5d922b6e1e213
tags: [domain/backend, stage/7, level/senior, topic/devops, topic/cicd, topic/gitlab, priority/nice]
reviewed:
next_review:
priority: nice
time: 5
---

# CI/CD для .NET-микросервисов и фронта в GitLab: пайплайн от MR до прода

↑ [[BE 7.6 DevOps для бэкенд-разработчика — деплой наших систем и CI-CD|7.6 DevOps для бэкенд-разработчика: деплой наших систем и CI/CD]] · ← [[BE 7.6.4 Конфигурация и секреты — env-файлы, Ansible-фабрика, окружения dev-staging-prod|Предыдущая]] · → [[BE 7.6.6 Миграции БД при деплое — Flyway, goose, EF и обратная совместимость|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



































> [!info] Зачем это на собесе
> Ждут описания пайплайна: какие стадии, какие проверки, как выкатывать.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Типовой пайплайн:

| Стадия | Задачи |
|---|---|
| Merge request | build, unit-тесты, линтеры, SAST, сканирование зависимостей, превью-окружение |
| main | те же + интеграционные тесты, сборка и push образа с тегом коммита |
| stage | автодеплой, smoke/e2e-тесты |
| prod | ручное подтверждение (manual) или автодеплой по политике, миграции, проверка health |
| после | уведомление, метки версии, мониторинг |

```yaml
stages: [test, build, deploy]
variables: { IMAGE: "$CI_REGISTRY_IMAGE/orders-api:$CI_COMMIT_SHORT_SHA" }

test:
  stage: test
  image: mcr.microsoft.com/dotnet/sdk:9.0
  script:
    - dotnet restore && dotnet build -c Release --no-restore
    - dotnet test -c Release --no-build --collect:"XPlat Code Coverage"
  coverage: '/Total\s+\|\s+(\d+(\.\d+)?)/'
  cache: { key: nuget, paths: [.nuget/] }

build_image:
  stage: build
  image: docker:27
  services: [docker:27-dind]
  script:
    - docker build -t "$IMAGE" .
    - docker push "$IMAGE"
  rules: [{ if: '$CI_COMMIT_BRANCH == "main"' }]

deploy_stage:
  stage: deploy
  script: [ansible-playbook -i inventories/stage deploy.yml -e image=$IMAGE]
  environment: { name: stage }
  rules: [{ if: '$CI_COMMIT_BRANCH == "main"' }]

deploy_prod:
  stage: deploy
  script: [ansible-playbook -i inventories/prod deploy.yml -e image=$IMAGE]
  environment: { name: production }
  when: manual
  rules: [{ if: '$CI_COMMIT_BRANCH == "main"' }]
```

Для фронтенда: `npm ci`, линтеры, unit-тесты, сборка статики, публикация в образ nginx или в объектное хранилище.

Практики: кэш зависимостей, параллельные джобы (`parallel`, `needs`), переменные CI (masked/protected) для секретов, окружения (`environment`) с историей деплоев, защищённые ветки, обязательное ревью, откат = повторный деплой предыдущего тега.

## Нюансы и подводные камни

- Секреты в логах CI: masked variables, не печатать окружение.
- Разные образы для stage и prod нарушают принцип «собрали один раз».
- Медленный пайплайн убивает практику частых релизов: кэш, параллелизм, разделение быстрых и медленных тестов.
- Без ручного шага или защит на prod случайный мерж уходит в прод.
- Runner'ы — точка доверия: изолируйте, ограничивайте права.

## Практика

1. Соберите пайплайн MR → main → stage → prod для сервиса.
2. Добавьте кэш NuGet и параллельные джобы, сократите время.
3. Настройте protected variables для prod-секретов.

## Вопросы с ответами

> [!question]- Чем continuous delivery отличается от continuous deployment?
> Delivery — код всегда готов к выкладке, выкладка вручную; deployment — автоматически в прод после проверок.

> [!question]- Как откатить релиз?
> Развернуть предыдущий образ (тег) и при необходимости откатить совместимую миграцию.

## Связанные темы

- [[N:3ea33104867981c0a409c221b337c688]]
- [[N:3ea3310486798133974de1e911b77d4c]]
