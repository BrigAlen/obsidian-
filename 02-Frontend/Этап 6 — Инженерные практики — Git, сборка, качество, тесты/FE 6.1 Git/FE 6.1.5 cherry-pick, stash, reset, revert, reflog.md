---
type: topic
domain: frontend
stage: 6
section: "6.1"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981c885fee3ee1fe7edbd
tags: [domain/frontend, stage/6, level/middle, topic/git, topic/recovery, topic/history, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# cherry-pick, stash, reset, revert, reflog

↑ [[FE 6.1 Git|6.1 Git]] · ← [[FE 6.1.4 Разрешение конфликтов|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Инструменты «спасения»: отменить коммит, вернуть потерянное, перенести изменения.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**cherry-pick** — перенос конкретного коммита в текущую ветку.

```bash
git cherry-pick a1b2c3d              # один коммит
git cherry-pick A^..B                # диапазон
git cherry-pick -x <hash>            # добавить ссылку на исходный коммит
```

Применение: hotfix из main в релизную ветку, перенос полезного коммита между ветками.

**stash** — временно спрятать незакоммиченные изменения.

```bash
git stash push -m "wip: filters" -u      # -u — включая неотслеживаемые
git stash list / git stash show -p stash@{0}
git stash pop / git stash apply / git stash drop
git stash branch new-branch stash@{0}
```

**reset** — перемещает ветку (и опционально индекс/рабочий каталог) на другой коммит.

| Режим | Указатель ветки | Индекс | Рабочий каталог | Использование |
|---|---|---|---|---|
| `--soft` | сдвигает | сохраняет | сохраняет | переупаковать коммиты |
| `--mixed` (по умолчанию) | сдвигает | сбрасывает | сохраняет | отменить `add` и коммит |
| `--hard` | сдвигает | сбрасывает | **сбрасывает** | выбросить всё (опасно) |

```bash
git reset --soft HEAD~1                # отменить коммит, оставить изменения в индексе
git reset --hard origin/main           # привести ветку к состоянию remote
```

**revert** — создаёт **новый коммит**, отменяющий изменения указанного; **безопасен для опубликованной истории**.

```bash
git revert a1b2c3d
git revert -m 1 <merge-commit>         # отменить merge (выбрать основного родителя)
```

**reflog** — журнал перемещений `HEAD` и веток (локально, ~90 дней): спасение после `reset --hard`, неудачного rebase, удалённой ветки.

```bash
git reflog
git reset --hard HEAD@{3}              # вернуться к состоянию до ошибки
git branch rescue <hash>               # восстановить «потерянный» коммит
```

Сводка: локальное «переписать» → `reset/rebase`, опубликованное «отменить» → `revert`; потеряли коммит → `reflog`; нужно «переключиться и не терять» → `stash`.

## Нюансы и подводные камни

- `reset --hard` удаляет незакоммиченные изменения без возможности восстановления (кроме IDE local history).
- `revert` отменённого merge затем требует «revert the revert» для повторного вливания.
- `cherry-pick` создаёт дубликат коммита: при последующем merge возможны конфликты.
- `stash` не по умолчанию включает неотслеживаемые файлы.
- Reflog локален и не переносится на другие машины.

## Практика

1. Намеренно сломайте историю `reset --hard` и восстановите через `reflog`.
2. Отмените merge-коммит через `revert -m 1`.
3. Перенесите hotfix-коммит в релизную ветку `cherry-pick -x`.

## Вопросы с ответами

> [!question]- Чем `reset` отличается от `revert`?
> `reset` переписывает историю ветки, `revert` добавляет новый коммит, отменяющий изменения, и безопасен для общих веток.

> [!question]- Как вернуть коммит после неудачного `reset --hard`?
> Найти хэш в `git reflog` и вернуться на него (`reset --hard` или новая ветка).

## Связанные темы

- [[N:3ea33104867981668a91f876e195135e]]
- [[N:3ea33104867981bab2c4fa6bd251ed0d]]
