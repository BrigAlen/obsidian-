---
type: topic
domain: devops
stage: 1
order: 18
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Git
reviewed: 
next_review: 
priority: should
time: 4
---

# Git для DevOps: ветки, теги, релизы, GitFlow и trunk-based

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> DevOps строит процессы вокруг Git: ветвление, релизы, теги. Нужно выбирать стратегию под команду.

## Основы, важные DevOps

```bash
git status; git log --oneline --graph --decorate --all
git switch -c feature/x; git switch main
git add -p; git commit -m "feat: ..."; git commit --amend
git fetch; git pull --rebase; git push -u origin feature/x
git stash; git stash pop
git rebase main; git merge --no-ff feature/x
git cherry-pick <sha>; git revert <sha>           # безопасная отмена публичного коммита
git reset --hard <sha>                             # только в локальной ветке!
git reflog                                         # спасение потерянных коммитов
git bisect start; git bisect bad; git bisect good v1.2.0    # поиск коммита-виновника
git diff main...feature/x; git blame file
```

**Правило**: не переписывайте историю опубликованных общих веток (нет `push --force` в `main`); `--force-with-lease` для своих веток.

## Теги и релизы

- **Аннотированный тег** фиксирует релиз: `git tag -a v1.4.0 -m "Release 1.4.0"` + `git push origin v1.4.0`; неаннотированный — лёгкая метка;
- **SemVer**: `MAJOR.MINOR.PATCH` (ломающие изменения / новые возможности / исправления), предрелизы `1.4.0-rc.1`;
- по тегу запускается релизный пайплайн: сборка образа с тегом, публикация артефактов, changelog (GitHub/GitLab Releases, `git-cliff`, `semantic-release`, `release-please`);
- теги **неизменяемы**: не перемещайте опубликованный тег;
- образ и артефакты связываются с коммитом: тег образа = версия + короткий SHA.

## Стратегии ветвления

### Git Flow

Ветки: `main` (продакшн), `develop` (интеграция), `feature/*`, `release/*`, `hotfix/*`.

- плюсы: чёткая структура для релизов по расписанию, поддержка нескольких версий;
- минусы: долгоживущие ветки, сложные слияния, медленная обратная связь, плохо сочетается с CD.

### GitHub Flow

`main` всегда готова к деплою; короткие feature-ветки → Pull Request → ревью → merge → деплой.

### GitLab Flow

GitHub Flow + **окружения/релизные ветки** (`staging`, `production`, `release/x.y`) для контролируемых выкаток.

### Trunk-Based Development

Все работают в `main` (trunk) короткоживущими ветками (часы–1–2 дня) или напрямую; незавершённое — за **feature flags**; частые интеграции; непрерывная доставка.

| | Git Flow | Trunk-based |
|---|---|---|
| Жизнь веток | недели | часы/дни |
| Интеграция | редкая, болезненная | постоянная |
| Релизы | по расписанию, из release-веток | из `main`, часто |
| Требования | процесс | сильные автотесты, feature flags, CI |
| Подходит | версионируемые продукты, несколько поддерживаемых версий, регулируемые отрасли | веб-сервисы, SaaS, CD |

DORA-исследования связывают trunk-based + CI/CD с лучшими показателями поставки.

## Защита веток и процесс

- **branch protection**: запрет прямого push в `main`, обязательные ревью и статусы CI, линейная история (`rebase/squash`), подписанные коммиты;
- **CODEOWNERS** — автоназначение ревьюеров;
- **Conventional Commits** (`feat:`, `fix:`, `BREAKING CHANGE`) → автоматические версии и changelog;
- **шаблоны PR/MR**, чек-листы;
- merge-стратегии: **merge commit** (сохраняет историю), **squash** (чистая история), **rebase** (линейная);
- **hooks**: pre-commit (линтеры, секреты: gitleaks), commit-msg (commitlint);
- не хранить в репозитории секреты, большие бинарники (Git LFS), артефакты сборки.

## Monorepo и полирепо

| | Monorepo | Polyrepo |
|---|---|---|
| Плюсы | атомарные изменения, общий код, единые инструменты | независимость, простые права |
| Минусы | нужен умный CI (запуск только затронутого: path filters, Nx, Turborepo, Bazel), рост репозитория | синхронизация версий, дублирование |

## GitOps

Git — источник истины для **инфраструктуры и конфигурации** (Helm/Kustomize/Terraform); изменения через PR; ArgoCD/Flux синхронизируют кластер с репозиторием.

## Практика отката

- откат релиза: `git revert`, выкатка предыдущего тега, откат по артефакту;
- hotfix: ветка от тега продакшна → исправление → merge в `main` и релиз;
- cherry-pick в поддерживаемые ветки.

## Типичные ситуации

| Ситуация | Решение |
|---|---|
| Закоммитили секрет | считать скомпрометированным: отозвать/ротировать; очистка истории (`git filter-repo`) — вторично |
| Конфликт при merge | разрешить, `git mergetool`, проверить сборку/тесты |
| Случайно удалили ветку | `git reflog` → `git branch name <sha>` |
| Большой репозиторий | `--depth 1`, `sparse-checkout`, partial clone (`--filter=blob:none`) в CI |

## Вопросы с ответами

> [!question]- Git Flow или Trunk-Based: что выбрать?
> Для веб-сервисов с частыми релизами — trunk-based с feature flags и сильным CI. Git Flow — для продуктов с версиями и релизами по графику, где нужно поддерживать несколько веток релизов.

> [!question]- Чем git revert отличается от git reset?
> `revert` создаёт новый коммит, отменяющий изменения (безопасен для общей истории); `reset` перемещает указатель ветки и переписывает историю (только для локальной работы).

> [!question]- Что такое SemVer и как его связать с тегами?
> Версионирование MAJOR.MINOR.PATCH; релиз отмечается аннотированным тегом `vX.Y.Z`, по которому пайплайн собирает и публикует артефакты; версию можно вычислять из Conventional Commits.
