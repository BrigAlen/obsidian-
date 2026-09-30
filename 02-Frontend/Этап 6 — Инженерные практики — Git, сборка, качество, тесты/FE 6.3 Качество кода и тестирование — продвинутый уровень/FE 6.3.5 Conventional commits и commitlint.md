---
type: topic
domain: frontend
stage: 6
section: "6.3"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981e380daebab0f2dae39
tags: [domain/frontend, stage/6, level/middle, topic/conventional-commits, topic/commitlint, topic/semver, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Conventional commits и commitlint

↑ [[FE 6.3 Качество кода и тестирование — продвинутый уровень|6.3 Качество кода и тестирование: продвинутый уровень]] · ← [[FE 6.3.4 Husky и lint-staged|Предыдущая]] · → [[FE 6.3.6 TDD и написание тестируемого кода|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Формат коммитов связывает историю, changelog и семантическое версионирование.

## Формат

```text
<type>(<scope>): <описание>

[тело]

[BREAKING CHANGE: ...]
```

Типы: `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `build`, `ci`, `chore`.

Примеры: `feat(auth): добавить вход по SSO`, `fix(table): не терять фильтр при пагинации`.

## Связь с SemVer

| Коммит | Версия |
|---|---|
| `fix` | patch (1.2.3 → 1.2.4) |
| `feat` | minor (1.2.3 → 1.3.0) |
| `BREAKING CHANGE` или `!` | major (1.2.3 → 2.0.0) |

## commitlint

```js
// commitlint.config.js
export default { extends: ['@commitlint/config-conventional'] }
```

```sh
# .husky/commit-msg
npx --no -- commitlint --edit "$1"
```

## Что это даёт

- автоматический **changelog** и версия (`semantic-release`, `release-please`, `changesets`);
- читаемая история и удобный поиск;
- триггеры в CI: `feat` → релиз.

## Нюансы

- при squash-merge важен заголовок PR — он станет коммитом;
- scope согласуйте в команде (пакет, модуль).

## Вопросы с ответами

> [!question]- Как коммиты связаны с версиями?
> `fix` увеличивает patch, `feat` — minor, breaking change — major. Инструменты релизов вычисляют версию из истории.
