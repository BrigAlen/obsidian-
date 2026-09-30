---
type: topic
domain: backend
stage: 2
section: "2.4"
order: 6
status: todo
level: middle
notion_id: 3ea331048679819b872aecead9568ecf
tags: [domain/backend, stage/2, level/middle, topic/dotnet, topic/testing, topic/ci, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Coverage (coverlet) и CI

↑ [[BE 2.4 Тестирование в .NET — основы|2.4 Тестирование в .NET — основы]] · ← [[BE 2.4.5 Тестируемый код — DI, TimeProvider, границы|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->















































> [!info] Зачем это на собесе
> Уточняющий вопрос: «какой у вас coverage и что он даёт?». Показывает, понимаете ли вы ограничения метрики.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Coverage показывает, какие строки и ветки выполнялись тестами. Это инструмент поиска непокрытых рисков, а не цель.

```bash
dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage
reportgenerator -reports:"coverage/**/coverage.cobertura.xml" -targetdir:coverage/report -reporttypes:Html
```

| Метрика | Значение |
|---|---|
| Line coverage | доля выполненных строк |
| Branch coverage | доля пройденных ветвей условий |
| Mutation score (Stryker.NET) | доля «мутантов», убитых тестами — проверяет качество проверок |

### Пример CI (GitHub Actions)

```yaml
- uses: actions/setup-dotnet@v4
  with: { dotnet-version: 9.0.x }
- run: dotnet restore
- run: dotnet build --no-restore -c Release
- run: dotnet test --no-build -c Release --collect:"XPlat Code Coverage" --logger trx
- uses: actions/upload-artifact@v4
  with: { name: coverage, path: "**/coverage.cobertura.xml" }
```

Порог покрытия в CI полезен как защита от регрессии («не падать ниже X»), но не как KPI.

## Нюансы и подводные камни

- 100% покрытия без assert-ов бесполезно; смотрите mutation testing.
- Исключайте сгенерированный код и DTO (`[ExcludeFromCodeCoverage]`).
- Интеграционные тесты в CI должны использовать контейнеры и изолированные данные.
- Держите быстрый набор (unit) на каждый push, медленные — на merge или ночью.
- Кэшируйте NuGet и параллельте сборку, чтобы CI оставался быстрым.

## Практика

1. Подключите coverlet и ReportGenerator, посмотрите отчёт по своему проекту.
2. Найдите методы с низким branch coverage и допишите тесты на ветки ошибок.
3. Запустите Stryker.NET на одном модуле и посмотрите выжившие мутанты.

## Вопросы с ответами

> [!question]- Достаточно ли 80% coverage?
> Число само по себе ничего не гарантирует: важны покрытые риски и качество проверок. Порог полезен как барьер от деградации.

> [!question]- Что такое mutation testing?
> Автоматически вносятся мелкие изменения в код; если тесты не падают, «мутант выжил», значит проверок не хватает.

> [!question]- Чем line coverage отличается от branch?
> Line считает выполненные строки, branch — обе стороны каждого условия; строка с `if` может быть «покрыта» без проверки ветки else.

## Связанные темы

- [[N:3ea33104867981f78191c12d951a2073]]
- [[N:3ea33104867981a2ad5ff285f83ecce9]]
