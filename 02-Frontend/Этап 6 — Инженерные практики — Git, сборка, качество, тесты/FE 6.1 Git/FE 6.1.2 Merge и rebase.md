---
type: topic
domain: frontend
stage: 6
section: "6.1"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981d2b219d09156d79abc
tags: [domain/frontend, stage/6, level/middle, topic/git, topic/merge, topic/rebase, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Merge и rebase

↑ [[FE 6.1 Git|6.1 Git]] · ← [[FE 6.1.1 Основные команды|Предыдущая]] · → [[FE 6.1.3 Git flow, trunk-based, feature branches|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Классика: в чём разница, когда что использовать и почему «золотое правило rebase».

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Оба способа объединяют изменения веток, но по-разному строят историю.

| | `merge` | `rebase` |
|---|---|---|
| Результат | merge-коммит с двумя родителями (или fast-forward) | линейная история: коммиты ветки переигрываются поверх целевой |
| История | сохраняет реальную хронологию, «ромбы» | чистая, линейная |
| Хэши коммитов | не меняются | меняются (новые коммиты) |
| Конфликты | разрешаются один раз | могут возникать на каждом переигрываемом коммите |
| Безопасность | безопасно для общих веток | переписывает историю: нельзя на опубликованных общих ветках |
| Отмена | `git revert -m 1 <merge>` | сложнее, `reflog` |

```bash
# merge: влить feature в main
git switch main && git merge --no-ff feature/x        # всегда создавать merge-коммит
git merge --ff-only feature/x                          # только если возможна перемотка

# rebase: обновить feature поверх main
git switch feature/x && git fetch && git rebase origin/main
git rebase --continue / --abort / --skip

# интерактивный rebase: причесать историю перед PR
git rebase -i HEAD~5                                   # pick, reword, squash, fixup, drop, edit, reorder
git commit --fixup <hash> && git rebase -i --autosquash origin/main
```

**Squash merge** (в PR): все коммиты ветки схлопываются в один — чистая история main, но теряется детализация.

Золотое правило rebase: **не переписывайте историю, которую уже получили другие** (`main`, общие ветки). Свою feature-ветку перед PR — можно и нужно.

Типичный процесс: работа в feature-ветке → `git pull --rebase`/`rebase origin/main` для актуальности → `rebase -i` для чистки → PR → merge/squash в main.

## Нюансы и подводные камни

- После `rebase` ветку нужно отправлять `push --force-with-lease`.
- Rebase ветки, от которой ответвились другие, ломает их основания.
- Слишком долгоживущие ветки приводят к болезненным конфликтам — вливайте `main` чаще.
- `git pull` по умолчанию делает merge: настройте `pull.rebase=true` осознанно.
- В PR-платформах squash скрывает авторство отдельных коммитов.

## Практика

1. Сравните граф после `merge --no-ff` и `rebase` на тестовом репозитории.
2. Соберите 5 коммитов в 2 через `rebase -i` (`squash`, `fixup`, `reword`).
3. Настройте `git config pull.rebase true`, `rebase.autoStash`.

## Вопросы с ответами

> [!question]- Чем rebase отличается от merge?
> Merge объединяет ветки merge-коммитом, сохраняя историю; rebase переигрывает коммиты поверх другой ветки, создавая линейную историю с новыми хэшами.

> [!question]- Почему нельзя делать rebase общих веток?
> Он меняет хэши коммитов, и у коллег история расходится с вашей.

## Связанные темы

- [[N:3ea33104867981fb91dce5485e0f1b19]]
- [[N:3ea3310486798182a186e56d50975b18]]
