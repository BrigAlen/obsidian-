---
type: topic
domain: frontend
stage: 6
section: "6.1"
order: 3
status: todo
level: middle
notion_id: 3ea3310486798182a186e56d50975b18
tags: [domain/frontend, stage/6, level/middle, topic/git, topic/branching, topic/workflow, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Git flow, trunk-based, feature branches

↑ [[FE 6.1 Git|6.1 Git]] · ← [[FE 6.1.2 Merge и rebase|Предыдущая]] · → [[FE 6.1.4 Разрешение конфликтов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Ждут сравнения стратегий и связи с частотой релизов и CI/CD.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Стратегия | Ветки | Когда |
|---|---|---|
| **Git flow** | `main`, `develop`, `feature/*`, `release/*`, `hotfix/*` | версионные релизы, мобильные приложения, редкие выкладки; тяжеловесна |
| **GitHub flow** | `main` + короткие feature-ветки + PR | непрерывная доставка веб-приложений |
| **GitLab flow** | `main` + окружения (`staging`, `production`) или релизные ветки | окружения и контролируемые релизы |
| **Trunk-based** | один `main` (trunk), очень короткие ветки (часы/1–2 дня) или прямые коммиты, **feature flags** | зрелый CI/CD, частые релизы, высокая автоматизация |

Trunk-based development:

- Небольшие частые интеграции в `main` (минимум раз в день).
- Незавершённый код скрывается **feature flags**.
- Обязательны быстрые автотесты, ревью небольших PR, защищённый `main`.
- Релизы — по тегу/ветке релиза (`release/1.4`) от trunk.
- Плюс: нет долгоживущих веток и «ада слияний»; минус: требует дисциплины и инфраструктуры.

Feature branches:

```text
main:      A──B──────────────G──H
            \                /
feature/x:   C──D──E──F─────/       (PR → review → CI → squash/merge)
```

Соглашения по именованию: `feature/ORD-123-order-filters`, `fix/…`, `hotfix/…`, `chore/…`, `release/x.y`.

Защита `main`: обязательные ревью, зелёный CI, запрет force-push, линейная история, CODEOWNERS, подписанные коммиты (по необходимости).

Выбор зависит от: частоты релизов, размера команды, зрелости тестов и CI, необходимости поддерживать несколько версий (тогда release-ветки).

## Нюансы и подводные камни

- Git flow с `develop` при непрерывной доставке создаёт лишнюю сложность.
- Долгоживущие feature-ветки накапливают конфликты и откладывают интеграцию.
- Feature flags — тоже долг: удаляйте после выката.
- Отсутствие быстрых тестов делает trunk-based опасным.
- Hotfix нужно обязательно вливать во все актуальные ветки.

## Практика

1. Опишите процесс вашей команды и предложите упрощение.
2. Настройте защиту `main` и шаблон PR.
3. Внедрите feature flag для незавершённой функции.

## Вопросы с ответами

> [!question]- Git flow или trunk-based?
> Git flow — для версионных релизов и редких выкладок; trunk-based — для частых релизов с сильным CI и feature flags.

> [!question]- Как выкатывать недоделанные фичи в trunk-based?
> Скрывать за feature flag и включать после готовности.

## Связанные темы

- [[N:3ea33104867981d2b219d09156d79abc]]
- [[N:3ea33104867981668a91f876e195135e]]
