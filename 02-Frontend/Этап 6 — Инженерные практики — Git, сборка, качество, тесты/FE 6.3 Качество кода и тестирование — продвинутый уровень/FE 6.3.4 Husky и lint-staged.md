---
type: topic
domain: frontend
stage: 6
section: "6.3"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981fab61ce7e3704b6476
tags: [domain/frontend, stage/6, level/middle, topic/husky, topic/lint-staged, topic/git-hooks, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Husky и lint-staged

↑ [[FE 6.3 Качество кода и тестирование — продвинутый уровень|6.3 Качество кода и тестирование: продвинутый уровень]] · ← [[FE 6.3.3 Stylelint|Предыдущая]] · → [[FE 6.3.5 Conventional commits и commitlint|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Спрашивают, как обеспечить качество до попадания кода в репозиторий и почему хуки нельзя считать единственной защитой.

## Суть

- **Husky** — управление git-хуками в репозитории (хуки живут в `.husky/`, версионируются).
- **lint-staged** — запуск команд **только на изменённых** (staged) файлах, что быстро.

## Установка

```sh
npm i -D husky lint-staged
npx husky init
```

```sh
# .husky/pre-commit
npx lint-staged
```

```json
{
  "lint-staged": {
    "*.{ts,vue}": ["eslint --fix", "prettier --write"],
    "*.{css,scss}": ["stylelint --fix", "prettier --write"],
    "*.{json,md}": "prettier --write"
  }
}
```

## Что вешать на какие хуки

| Хук | Задача |
|---|---|
| `pre-commit` | lint-staged, быстрая проверка |
| `commit-msg` | commitlint |
| `pre-push` | typecheck, связанные тесты |

## Нюансы

- хуки можно обойти (`--no-verify`), поэтому **CI — главная защита**, хуки лишь ускоряют обратную связь;
- тяжёлые проверки в pre-commit раздражают — переносите в pre-push и CI;
- `prepare`-скрипт в `package.json` ставит хуки после `npm install`;
- в monorepo lint-staged настраивается на уровне пакетов.

## Вопросы с ответами

> [!question]- Почему lint-staged, а не линтить весь проект в pre-commit?
> Полный прогон медленный. lint-staged обрабатывает только изменённые файлы — быстро и достаточно, чтобы новый код был чистым.

> [!question]- Можно ли полагаться только на хуки?
> Нет. Их обходят `--no-verify`, они не стоят у нового участника. Обязательная проверка — в CI.
