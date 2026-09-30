---
type: topic
domain: frontend
stage: 6
section: "6.2"
order: 6
status: todo
level: middle
notion_id: 3ea33104867981bb957ece3a6db635e6
tags: [domain/frontend, stage/6, level/middle, topic/build, topic/monorepo, topic/pnpm, topic/nx, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Monorepo: pnpm workspaces, Nx, Turborepo

↑ [[FE 6.2 Сборка и инфраструктура — Vite, monorepo, CI-CD|6.2 Сборка и инфраструктура: Vite, monorepo, CI/CD]] · ← [[FE 6.2.5 Пакетные менеджеры — npm, yarn, pnpm, lock-файлы, semver|Предыдущая]] · → [[FE 6.2.7 Общая библиотека компонентов и composables|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Организация нескольких приложений и библиотек в одном репозитории.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Monorepo** — один репозиторий для нескольких пакетов/приложений (web, admin, ui-kit, api-client, конфигурации).

| Плюсы | Минусы |
|---|---|
| атомарные изменения по нескольким пакетам | размер репозитория, время CI без кэша |
| единые версии зависимостей и настройки | права доступа (всё в одном репозитории) |
| простой шаринг кода без публикации | сложнее онбординг |
| единые CI/линтеры/скрипты | нужны инструменты (кэш, affected) |

```text
apps/web, apps/admin
packages/ui, packages/api-client, packages/config-eslint, packages/config-ts
pnpm-workspace.yaml, package.json, turbo.json / nx.json, tsconfig.base.json
```

```yaml
# pnpm-workspace.yaml
packages: ["apps/*", "packages/*"]
```

```json
// apps/web/package.json
{ "dependencies": { "@acme/ui": "workspace:*", "@acme/api-client": "workspace:*" } }
```

| Инструмент | Роль |
|---|---|
| **pnpm workspaces** | установка и связывание пакетов (`workspace:*`), `pnpm -F web build`, `pnpm -r test` |
| **Turborepo** | оркестрация задач (`turbo run build test lint`), граф зависимостей, кэш результатов (локальный и удалённый), параллелизм |
| **Nx** | то же + генераторы, `affected` (только затронутые проекты), графы, плагины, module boundaries |
| **Lerna** | публикация версий (сейчас поверх Nx) |
| **Changesets** | версионирование и changelog |

```json
// turbo.json
{ "tasks": { "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] }, "test": { "dependsOn": ["build"] }, "lint": {}, "dev": { "cache": false, "persistent": true } } }
```

Практики:

- Внутренние пакеты — TypeScript-проекты (`references`) или исходники без сборки (`exports` на `src`) с Vite alias.
- Единые конфиги (ESLint, Prettier, tsconfig) как пакеты.
- **Affected**: в CI запускать только затронутые задачи.
- Кэш сборки/тестов (Remote Cache) сокращает CI в разы.
- Границы модулей: правила импортов (`nx enforce-module-boundaries`, ESLint).
- Версионирование: независимое или фиксированное, Changesets.

## Нюансы и подводные камни

- Циклические зависимости между пакетами.
- «Фантомные» зависимости: пакет использует зависимость, объявленную не у себя (pnpm строгий — помогает).
- Единая версия зависимости на весь репозиторий vs потребности приложений.
- Без кэша и affected CI становится очень медленным.
- Монорепо не отменяет границ: без правил всё связывается со всем.

## Практика

1. Создайте pnpm workspace с приложением и общим `ui` пакетом.
2. Настройте Turborepo с кэшем и `dependsOn`.
3. Запустите в CI только затронутые пакеты.

## Вопросы с ответами

> [!question]- Зачем monorepo?
> Общий код и конфигурации, атомарные изменения по нескольким пакетам, единый CI.

> [!question]- Что делает Turborepo/Nx?
> Оркестрируют задачи по графу зависимостей, кэшируют результаты и запускают только затронутое.

## Связанные темы

- [[N:3ea33104867981a0ade9f88b2d4cc268]]
- [[N:3ea331048679818d8857d000567e48fe]]
