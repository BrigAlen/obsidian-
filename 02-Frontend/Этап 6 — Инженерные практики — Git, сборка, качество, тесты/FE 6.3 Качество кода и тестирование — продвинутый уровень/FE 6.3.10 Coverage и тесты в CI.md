---
type: topic
domain: frontend
stage: 6
section: "6.3"
order: 10
status: todo
level: middle
notion_id: 3ea33104867981d38ce9c413285a4dc4
tags: [domain/frontend, stage/6, level/middle, topic/coverage, topic/ci, topic/vitest, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Coverage и тесты в CI

↑ [[FE 6.3 Качество кода и тестирование — продвинутый уровень|6.3 Качество кода и тестирование: продвинутый уровень]] · ← [[FE 6.3.9 Тестирование доступности — axe|Предыдущая]] · → [[FE 6.3.11 Code review — что и как проверять|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Покрытие — метрика, которой легко манипулировать. Важно показать, как использовать её разумно.

## Метрики покрытия

Строки, ветки (branches), функции, операторы. **Branch coverage** информативнее line coverage.

## Vitest

```ts
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      include: ['src/**/*.{ts,vue}'],
      exclude: ['src/**/*.stories.ts', 'src/main.ts'],
      thresholds: { lines: 80, branches: 70 },
    },
  },
})
```

## Тесты в CI

```yaml
- run: npm ci
- run: npx vitest run --coverage
- run: npx playwright install --with-deps chromium
- run: npx playwright test
- uses: actions/upload-artifact@v4
  if: always()
  with: { name: playwright-report, path: playwright-report }
```

## Подходы

- **порог** на новый код (diff coverage), а не на всю историю;
- отчёт в PR (Codecov, SonarQube);
- быстрые тесты — на каждый push, E2E — на PR или nightly;
- шардинг и параллелизм: `--shard=1/4`;
- кэш зависимостей и браузеров.

## Ловушки

100% покрытие не гарантирует качества: тест без assertion считается покрытием. Погоня за процентом стимулирует бессмысленные тесты. Дополняйте мутационным тестированием (Stryker).

## Вопросы с ответами

> [!question]- Достаточно ли высокого покрытия?
> Нет. Покрытие показывает, что код выполнялся, но не то, что поведение проверено. Смотрите на ветки, критические пути и качество assert.

> [!question]- Как ускорить тесты в CI?
> Параллелизм и шардинг, кэш зависимостей, запуск только затронутых пакетов, разделение быстрых и медленных наборов.
