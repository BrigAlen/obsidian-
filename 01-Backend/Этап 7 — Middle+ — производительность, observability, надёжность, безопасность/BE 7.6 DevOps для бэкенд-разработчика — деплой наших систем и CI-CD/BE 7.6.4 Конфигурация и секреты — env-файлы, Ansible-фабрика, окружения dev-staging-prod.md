---
type: topic
domain: backend
stage: 7
section: "7.6"
order: 4
status: todo
level: senior
notion_id: 3ea33104867981c0a409c221b337c688
tags: [domain/backend, stage/7, level/senior, topic/devops, topic/configuration, topic/ansible, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Конфигурация и секреты: env-файлы, Ansible-фабрика, окружения dev/staging/prod

↑ [[BE 7.6 DevOps для бэкенд-разработчика — деплой наших систем и CI-CD|7.6 DevOps для бэкенд-разработчика: деплой наших систем и CI/CD]] · ← [[BE 7.6.3 Как поднимается Clinic — docker compose, Makefile, порядок запуска, healthcheck|Предыдущая]] · → [[BE 7.6.5 CI-CD для .NET-микросервисов и фронта в GitLab — пайплайн от MR до прода|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


































> [!info] Зачем это на собесе
> Как управлять конфигурацией нескольких окружений без копипаста и утечек секретов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново; описан общий подход «шаблоны + инвентарь окружений».

## Объяснение

Принцип 12-factor: **конфигурация в окружении, код один**.

| Слой | Что | Где |
|---|---|---|
| Код и образ | одинаковы везде | registry |
| Несекретная конфигурация | адреса, флаги, лимиты | шаблоны env-файлов, ConfigMap |
| Секреты | пароли, ключи | Vault/секреты CI/зашифрованные vars (ansible-vault, SOPS) |
| Различия окружений | значения переменных | инвентарь `dev`/`staging`/`prod` |

**Ansible как «фабрика конфигурации»**: из шаблонов Jinja2 и инвентаря окружения генерируются `.env` и `docker-compose`-файлы для каждого сервера.

```yaml
# inventories/prod/group_vars/all.yml
orders_db_host: pg-prod.internal
orders_replicas: 4
# inventories/prod/group_vars/vault.yml  (ansible-vault encrypt)
orders_db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256...

# templates/orders.env.j2
ConnectionStrings__Default=Host={{ orders_db_host }};Database=orders;Password={{ orders_db_password }}
Replicas={{ orders_replicas }}

# деплой
ansible-playbook -i inventories/prod deploy.yml --tags orders
```

Правила:

- Значения по умолчанию в `dev`, явные значения в `prod`.
- Единый список ключей конфигурации; валидация при старте (`ValidateOnStart`, см. [[N:3ea331048679814dbaadc2a67ef314e5]]).
- Проверка отсутствующих значений в CI (шаблон рендерится для каждого окружения).
- Секреты отдельно от остальной конфигурации, с ограничением доступа и ротацией (см. [[N:3ea331048679819c9bb7c741225859ca]]).

## Нюансы и подводные камни

- Расхождение окружений («на stage работает») — ведите различия минимальными и явными.
- Один общий `.env` на все окружения приводит к использованию prod-данных в dev.
- Незашифрованные vault-файлы в git — утечка.
- Изменение конфигурации требует перезапуска (или конфигурации с reload).

## Практика

1. Сгенерируйте env-файлы двух окружений из одного шаблона и инвентаря.
2. Зашифруйте секреты ansible-vault/SOPS.
3. Добавьте проверку в CI: рендер шаблонов и валидация обязательных ключей.

## Вопросы с ответами

> [!question]- Как управлять конфигурацией для нескольких окружений?
> Один образ, шаблоны конфигурации и инвентарь значений по окружениям, секреты — отдельно и зашифрованно.

> [!question]- Что такое 12-factor config?
> Конфигурация хранится в окружении и отделена от кода.

## Связанные темы

- [[N:3ea33104867981a9874fd15bb01e9c43]]
- [[N:3ea33104867981e1abd5d922b6e1e213]]
