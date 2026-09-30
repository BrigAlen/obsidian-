---
type: topic
domain: frontend
stage: 6
section: "6.2"
order: 10
status: todo
level: middle
notion_id: 71baa0cafa97476da6dc9a5a3b7bb970
tags: [domain/frontend, stage/6, level/middle, topic/release, topic/spa, topic/cdn, topic/sentry, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Релиз SPA: runtime config, source maps, CDN-кэш и rollback

↑ [[FE 6.2 Сборка и инфраструктура — Vite, monorepo, CI-CD|6.2 Сборка и инфраструктура: Vite, monorepo, CI/CD]] · ← [[FE 6.2.9 Docker и nginx для SPA|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Вопрос «как вы выкатываете фронтенд» проверяет, понимаете ли вы разницу между сборкой и конфигурацией, кэшированием и откатом.

## Главная идея

Один и тот же артефакт сборки (Docker-образ или архив статики) должен работать на dev, stage и prod. Всё окруженческое — **runtime config**, а не build-time переменные.

## Runtime config

Проблема: `import.meta.env.VITE_API_URL` вшивается в бандл при сборке. Для нового окружения пришлось бы пересобирать.

Решение: файл `config.json` рядом с `index.html`, который приложение читает при старте. Его генерирует entrypoint контейнера из переменных окружения.

```sh
# docker-entrypoint.d/40-runtime-config.sh
printf '{ "apiUrl": "%s", "sentryDsn": "%s", "release": "%s" }\n' \
  "$API_URL" "$SENTRY_DSN" "$RELEASE" > /usr/share/nginx/html/config.json
```

```ts
// main.ts
const config = await fetch('/config.json', { cache: 'no-store' }).then(r => r.json())
const app = createApp(App)
app.provide(CONFIG_KEY, config)
app.mount('#app')
```

Важно: `config.json` — не для секретов, он публичный.

## Кэширование

| Файл | Заголовок | Почему |
|---|---|---|
| `index.html` | `no-cache` | Всегда проверять, чтобы получить новые хэши |
| `assets/*.[hash].js/css` | `public, max-age=31536000, immutable` | Имя содержит хэш содержимого |
| `config.json` | `no-store` | Меняется без пересборки |

Порядок выкладки: сначала новые `assets`, потом `index.html`. Иначе пользователь получит HTML, ссылающийся на ещё не загруженные файлы.

## Проблема старых чанков

После деплоя у открытой вкладки остаются ссылки на старые чанки, которых на сервере уже нет → ошибка `Failed to fetch dynamically imported module`.

- храните предыдущие 1–2 релиза assets на CDN;
- в роутере перехватывайте ошибку и делайте `location.reload()`;
- Vite генерирует событие `vite:preloadError`.

```ts
window.addEventListener('vite:preloadError', () => location.reload())
```

## Source maps

- собираем с `build.sourcemap: 'hidden'` — карты создаются, но ссылка на них в бандле не добавляется;
- загружаем в Sentry с привязкой к `release`, затем **удаляем из публичной раздачи**;
- так пользователь не видит исходники, а стек-трейсы в Sentry читаемы.

## Rollback

1. Артефакты версионируются (тег образа = git sha).
2. Откат = переключение на предыдущий тег / переопределение alias на CDN.
3. Пересборка не нужна — поэтому важен runtime config.
4. Если релиз затронул API-контракт, откат фронта должен быть совместим с текущим бэкендом.

## Фичефлаги и канареечные релизы

- новые фичи прячем за флагом — включаем постепенно без деплоя;
- canary: 5% трафика на новую версию, наблюдаем ошибки в Sentry и Web Vitals, затем расширяем.

## Вопросы с ответами

> [!question]- Почему нельзя хранить API URL в VITE_ переменной?
> Она вшивается в бандл при сборке, и для каждого окружения потребуется отдельная сборка. Артефакт перестаёт быть идентичным, растёт риск «работало на stage, сломалось на prod».

> [!question]- Почему index.html не кэшируют, а хэшированные файлы кэшируют навсегда?
> В index.html лежат ссылки на текущие хэши, его надо проверять каждый раз. Имя файла с хэшем меняется вместе с содержимым, поэтому его безопасно кэшировать как immutable.

> [!question]- Что такое hidden source maps?
> Карты создаются при сборке, но бандл не содержит комментарий `sourceMappingURL`. Карты уходят в Sentry, а не пользователям.

> [!question]- Как откатить релиз фронтенда?
> Переключить alias или тег на предыдущий артефакт. Пересборка не нужна. Проверить совместимость с текущей версией API.
