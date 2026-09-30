---
type: topic
domain: frontend
stage: 6
section: "6.2"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981a0ade9f88b2d4cc268
tags: [domain/frontend, stage/6, level/middle, topic/build, topic/npm, topic/pnpm, topic/semver, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Пакетные менеджеры: npm, yarn, pnpm, lock-файлы, semver

↑ [[FE 6.2 Сборка и инфраструктура — Vite, monorepo, CI-CD|6.2 Сборка и инфраструктура: Vite, monorepo, CI/CD]] · ← [[FE 6.2.4 Переменные окружения и режимы сборки|Предыдущая]] · → [[FE 6.2.6 Monorepo — pnpm workspaces, Nx, Turborepo|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Воспроизводимость сборок и безопасность зависимостей.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Менеджер | Особенности |
|---|---|
| npm | стандарт с Node.js, плоский `node_modules` |
| Yarn (Classic v1, Berry v2+) | workspaces, Plug'n'Play (Berry), zero-installs |
| **pnpm** | контентно-адресуемое хранилище + жёсткие ссылки: экономия диска, скорость, строгая структура (нет «фантомных» зависимостей) |
| Bun | быстрый рантайм и менеджер |

**semver** `MAJOR.MINOR.PATCH`: major — ломающие изменения, minor — обратно совместимые новые возможности, patch — исправления.

| Диапазон | Значение |
|---|---|
| `1.2.3` | ровно |
| `^1.2.3` | `>=1.2.3 <2.0.0` (по умолчанию в npm) |
| `~1.2.3` | `>=1.2.3 <1.3.0` |
| `>=`, `*`, `latest` | опасно широкие |
| Pre-release `1.0.0-beta.2` | нестабильные |

**Lock-файл** (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) фиксирует точное дерево зависимостей и хэши — воспроизводимая установка. **Коммитьте lock-файл.**

```bash
npm ci                     # строго по lock-файлу, чистая установка (CI)
npm install                # может обновить lock
pnpm install --frozen-lockfile
npm outdated / npm update / npx npm-check-updates -u
npm audit --omit=dev / npm audit fix
npm ls <pkg> / npm why <pkg>          # почему пакет в дереве
npm overrides / pnpm.overrides         # принудительные версии транзитивных зависимостей
```

Разделы `package.json`: `dependencies` (прод), `devDependencies` (сборка/тесты), `peerDependencies` (ожидаемые версии у хоста, для библиотек), `optionalDependencies`, `engines`, `scripts`, `sideEffects`, `exports`, `type`.

Безопасность цепочки поставок: `npm audit`, Dependabot/Renovate, подтверждение обновлений тестами, минимальные права установочных скриптов (`ignore-scripts`), проверка новых пакетов (typosquatting), **provenance**, защита от dependency confusion (scoped-пакеты, приватный реестр).

## Нюансы и подводные камни

- `npm install` вместо `npm ci` в CI даёт невоспроизводимые сборки.
- Смешивание менеджеров в одном проекте портит lock-файлы.
- `^` для `0.x` версий ведёт себя строже (`^0.2.3` = `>=0.2.3 <0.3.0`).
- Конфликты peer-зависимостей: `--legacy-peer-deps` — временный костыль.
- Доверие к `postinstall`-скриптам сторонних пакетов — риск.

## Практика

1. Проверьте, что в CI используется `npm ci`/`--frozen-lockfile` и lock-файл закоммичен.
2. Найдите причину появления пакета через `npm why`.
3. Настройте Renovate/Dependabot с группировкой обновлений.

## Вопросы с ответами

> [!question]- Чем `npm ci` отличается от `npm install`?
> `ci` устанавливает строго по lock-файлу и удаляет `node_modules`, гарантируя воспроизводимость; `install` может изменить lock.

> [!question]- Что означает `^1.2.3`?
> Любая версия от 1.2.3 до, но не включая, 2.0.0.

## Связанные темы

- [[N:3ea33104867981ae9b4bf9d29143eb13]]
- [[N:3ea33104867981bb957ece3a6db635e6]]
