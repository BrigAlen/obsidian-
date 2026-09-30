---
type: topic
domain: frontend
stage: 6
section: "6.3"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981daa4f4e2c5b860c071
tags: [domain/frontend, stage/6, level/middle, topic/prettier, topic/formatting, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Prettier

↑ [[FE 6.3 Качество кода и тестирование — продвинутый уровень|6.3 Качество кода и тестирование: продвинутый уровень]] · ← [[FE 6.3.1 ESLint|Предыдущая]] · → [[FE 6.3.3 Stylelint|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Проверяют, что вы разделяете форматирование и качество кода, и знаете, как убрать споры о стиле в code review.

## Суть

Prettier — opinionated-форматтер. Он полностью переписывает код по единым правилам, и обсуждение отступов и запятых уходит из review.

## Настройка

```json
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 100,
  "trailingComma": "all"
}
```

Опций намеренно мало. Хорошая практика: закоммитить `.prettierrc` и `.prettierignore` (`dist`, `coverage`, lock-файлы).

## Интеграция

- в редакторе — format on save;
- в git-хуке — через lint-staged (`prettier --write`);
- в CI — `prettier --check .`: падает, если код не отформатирован;
- с ESLint — отдельными шагами, а не плагином внутри ESLint (быстрее и проще диагностика).

## Нюансы

- переформатирование всего репозитория делайте **одним коммитом** и добавьте его в `.git-blame-ignore-revs`, чтобы `git blame` не ломался;
- плагины: `prettier-plugin-tailwindcss` для сортировки классов;
- Vue SFC и шаблоны поддерживаются из коробки.

## Вопросы с ответами

> [!question]- Зачем Prettier, если есть ESLint?
> Он снимает споры о стиле и форматирует быстрее и предсказуемее. Правила стиля из ESLint только дублировали бы его.

> [!question]- Как не сломать git blame при массовом форматировании?
> Вынести форматирование в отдельный коммит и добавить его хэш в `.git-blame-ignore-revs`; GitHub и git его учитывают.
