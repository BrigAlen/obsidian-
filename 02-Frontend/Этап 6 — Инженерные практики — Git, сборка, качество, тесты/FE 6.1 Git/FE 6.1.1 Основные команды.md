---
type: topic
domain: frontend
stage: 6
section: "6.1"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981fb91dce5485e0f1b19
tags: [domain/frontend, stage/6, level/middle, topic/git, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Основные команды

↑ [[FE 6.1 Git|6.1 Git]] · → [[FE 6.1.2 Merge и rebase|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Базовые вопросы: как устроен Git, чем `fetch` отличается от `pull`, что такое индекс.

## Объяснение

Git — распределённая система контроля версий: история — граф коммитов, ветка — подвижный указатель на коммит, `HEAD` — текущая позиция.

Три области: **рабочий каталог** → `git add` → **индекс (staging)** → `git commit` → **репозиторий**.

```bash
git init / git clone <url>
git status -sb                         # состояние кратко
git add -p                             # выборочное добавление кусков (patch)
git commit -m "feat(orders): add filters"
git commit --amend --no-edit           # дополнить последний коммит (только неопубликованный)

git log --oneline --graph --decorate --all
git diff / git diff --staged / git diff main...feature
git show <hash>

git branch feature/x && git switch feature/x     # или git switch -c feature/x
git switch main
git restore file.ts / git restore --staged file.ts     # отменить правки / убрать из индекса

git remote -v
git fetch origin                        # скачать изменения без слияния
git pull --rebase origin main           # fetch + rebase (чистая история)
git push -u origin feature/x
git push --force-with-lease             # безопасная принудительная отправка
git tag -a v1.2.0 -m "release"
git blame file.ts / git bisect start    # поиск коммита, внесшего баг
```

| Команда | Смысл |
|---|---|
| `fetch` | скачивает объекты и обновляет `origin/*`, рабочий каталог не трогает |
| `pull` | `fetch` + `merge` (или `rebase` с `--rebase`) |
| `clone` | копия репозитория |
| `.gitignore` | файлы, которые не отслеживаются (`node_modules`, `dist`, `.env`) |
| `.gitattributes` | нормализация концов строк, LFS |

Хорошие коммиты: небольшие, атомарные, с понятным сообщением (см. Conventional Commits), проходящие тесты.

## Нюансы и подводные камни

- `git add .` добавляет лишнее (секреты, артефакты): просматривайте `git status`/`git diff --staged`.
- Не переписывайте опубликованную общую историю (`--amend`, `rebase`, `push -f`) без договорённости.
- `.env` и секреты в истории остаются даже после удаления: нужна ротация и чистка истории.
- Разные окончания строк (CRLF/LF) — `core.autocrlf`, `.gitattributes`.
- Большие бинарные файлы — Git LFS.

## Практика

1. Создайте репозиторий, сделайте серию коммитов, посмотрите граф.
2. Используйте `git add -p` и `git restore --staged`.
3. Найдите баг через `git bisect`.

## Вопросы с ответами

> [!question]- Чем `git fetch` отличается от `git pull`?
> `fetch` только скачивает изменения, `pull` дополнительно объединяет их с текущей веткой.

> [!question]- Что такое индекс (staging area)?
> Промежуточная область, в которой формируется содержимое следующего коммита.

## Связанные темы

- [[N:3ea331048679813da123f4a332bbf8c1]]
- [[N:3ea33104867981d2b219d09156d79abc]]
