---
type: topic
domain: frontend
stage: 6
section: "6.3"
order: 3
status: todo
level: middle
notion_id: 3ea3310486798193bd2fcb0b5e37778c
tags: [domain/frontend, stage/6, level/middle, topic/stylelint, topic/css, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Stylelint

↑ [[FE 6.3 Качество кода и тестирование — продвинутый уровень|6.3 Качество кода и тестирование: продвинутый уровень]] · ← [[FE 6.3.2 Prettier|Предыдущая]] · → [[FE 6.3.4 Husky и lint-staged|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Тема средняя по приоритету: показывает, что вы заботитесь о CSS так же, как о TypeScript.

## Суть

Stylelint — линтер для CSS, SCSS, Vue-стилей. Ловит невалидные свойства, дубли селекторов, недопустимые единицы, слишком высокую специфичность.

## Конфиг

```json
{
  "extends": ["stylelint-config-standard-scss", "stylelint-config-recommended-vue"],
  "rules": {
    "selector-max-id": 0,
    "declaration-no-important": true,
    "selector-class-pattern": "^[a-z][a-z0-9]*(-[a-z0-9]+)*(__[a-z0-9-]+)?(--[a-z0-9-]+)?$"
  }
}
```

## Полезные правила

- запрет `!important` и id-селекторов;
- проверка формата имён классов (БЭМ или kebab-case);
- порядок свойств — `stylelint-config-recess-order`;
- запрет неизвестных свойств и опечаток (`colr`).

## Практика

- запуск в pre-commit для изменённых `.css/.scss/.vue`;
- `--fix` для автоправок;
- совместим с Prettier: форматирование отдаём Prettier.

## Подключение в проекте

```sh
npm i -D stylelint stylelint-config-standard-scss stylelint-config-recommended-vue postcss-html
npx stylelint "src/**/*.{css,scss,vue}" --fix
```

В `package.json` добавьте скрипт `"lint:css": "stylelint \"src/**/*.{css,scss,vue}\""` и запускайте его в CI вместе с ESLint. Для `.vue` нужен парсер `postcss-html`, для SCSS — конфиг `stylelint-config-standard-scss`.

## Как внедрять в существующий проект

1. Начать с рекомендуемого пресета и запустить `--fix`: половина замечаний уйдёт автоматически.
2. Оставшиеся правила включать по одному, начиная с ошибок (неизвестные свойства, дубли).
3. Для старого кода временно использовать `overrides` и постепенно сужать исключения.
4. Правила стиля не спорить: форматирование отдаётся Prettier, Stylelint отвечает за качество и договорённости.

## Что ловит на практике

| Проблема | Правило |
|---|---|
| опечатка в свойстве | `property-no-unknown` |
| дублирующиеся селекторы | `no-duplicate-selectors` |
| переопределение стилей `!important` | `declaration-no-important` |
| слишком высокая специфичность | `selector-max-specificity` |
| недопустимая единица или значение | `unit-no-unknown`, `declaration-property-value-no-unknown` |

## Вопросы с ответами

> [!question]- Зачем линтить CSS?
> CSS ломается тихо: опечатка в свойстве просто игнорируется. Линтер находит такие ошибки и держит специфичность под контролем.
