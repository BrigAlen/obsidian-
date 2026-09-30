---
type: topic
domain: frontend
stage: 6
section: "6.2"
order: 8
status: todo
level: middle
notion_id: 3ea33104867981149d11e5185d139a9b
tags: [domain/frontend, stage/6, level/middle, topic/ci-cd, topic/frontend, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# CI/CD для фронтенда

↑ [[FE 6.2 Сборка и инфраструктура — Vite, monorepo, CI-CD|6.2 Сборка и инфраструктура: Vite, monorepo, CI/CD]] · ← [[FE 6.2.7 Общая библиотека компонентов и composables|Предыдущая]] · → [[FE 6.2.9 Docker и nginx для SPA|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Как выглядит пайплайн фронтенда: проверки, сборка, превью-окружения и деплой.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Этапы пайплайна:

| Стадия | Действия |
|---|---|
| Установка | `npm ci` с кэшем (`~/.npm`/pnpm store), Node из `.nvmrc` |
| Проверки | `eslint`, `prettier --check`, `stylelint`, `vue-tsc --noEmit` |
| Тесты | unit/component (Vitest) + coverage |
| Сборка | `vite build` (артефакт `dist`) |
| Безопасность | `npm audit`, SAST, secret scanning, проверка лицензий |
| E2E | Playwright на превью-окружении/против контейнера |
| Качество производительности | Lighthouse CI, size-limit (бюджет размера) |
| Артефакт | образ Docker (nginx + `dist`) или статические файлы в бакет |
| Deploy | preview на MR, stage (авто), prod (вручную/по тегу) |
| Пост-проверки | smoke-тест, мониторинг ошибок (Sentry release), откат |

```yaml
# GitHub Actions
name: ci
on: { pull_request: {}, push: { branches: [main] } }
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version-file: .nvmrc, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint && pnpm typecheck && pnpm test --coverage
      - run: pnpm build
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist }
  e2e:
    needs: verify
    steps: [ ... playwright install --with-deps, pnpm e2e ... ]
  deploy:
    needs: [verify, e2e]
    if: github.ref == 'refs/heads/main'
    environment: production          # ручное подтверждение
    steps: [ ... docker build/push, deploy ... ]
```

Практики:

- Быстрый фидбек: параллельные джобы, кэш, affected-подход в monorepo.
- Превью-окружение на каждый MR (Netlify/Vercel/Cloudflare Pages или свой стенд) для ревью дизайна и e2e.
- Один артефакт на все окружения + runtime-конфигурация.
- Версия/коммит в приложении (`__APP_VERSION__`), source maps → Sentry (не публично).
- Защищённые переменные и секреты CI; принцип наименьших прав токенов.
- Кэш зависимостей и сборки, ограничение параллельных прогонов (concurrency cancel).
- Пороги качества как блокирующие проверки (coverage, размер бандла, a11y).

## Нюансы и подводные камни

- Нестабильные e2e-тесты подрывают доверие к CI.
- Секреты в логах/артефактах.
- Разные версии Node локально и в CI — фиксируйте `.nvmrc`/`engines`.
- Слишком долгий пайплайн — разработчики обходят его.
- Автодеплой в prod без защиты и метрик отката.

## Практика

1. Соберите пайплайн: lint → typecheck → test → build → artifact.
2. Добавьте превью-окружения для MR.
3. Настройте Lighthouse CI и size-limit как блокирующие проверки.

## Вопросы с ответами

> [!question]- Что должно быть в CI фронтенда?
> Установка по lock-файлу, линтеры, проверка типов, тесты, сборка и артефакт; далее e2e, безопасность и деплой.

> [!question]- Зачем превью-окружения?
> Позволяют проверить изменения в реальной среде до слияния (ревью, e2e, согласование дизайна).

## Связанные темы

- [[N:3ea331048679818d8857d000567e48fe]]
- [[N:3ea33104867981fe938fc211e813641e]]
