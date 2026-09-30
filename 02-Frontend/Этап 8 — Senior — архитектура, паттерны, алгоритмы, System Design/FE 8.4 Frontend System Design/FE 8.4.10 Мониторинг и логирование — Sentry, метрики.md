---
type: topic
domain: frontend
stage: 8
section: "8.4"
order: 10
status: todo
level: senior
notion_id: 3ea331048679819d9b15df87b6ff7f7a
tags: [domain/frontend, stage/8, level/senior, topic/monitoring, topic/sentry, topic/observability, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Мониторинг и логирование: Sentry, метрики

↑ [[FE 8.4 Frontend System Design|8.4 Frontend System Design]] · ← [[FE 8.4.9 Кейс — конструктор форм|Предыдущая]] · → [[FE 8.4.11 Feature flags и A-B-тесты|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Frontend observability: как узнать о проблемах раньше пользователей и связать ошибки с релизом и трассой.

## Что собираем

| Сигнал | Инструмент |
|---|---|
| Ошибки JS и необработанные промисы | Sentry, Rollbar, Bugsnag |
| Производительность (Web Vitals, транзакции) | Sentry Performance, web-vitals, Datadog RUM |
| Пользовательские события | аналитика, продуктовые метрики |
| Логи | клиентский логгер → сервер |
| Сессии | session replay (с маскированием) |
| Трассировки | OpenTelemetry (связь с бэкендом) |

## Sentry во Vue

```ts
import * as Sentry from '@sentry/vue'

Sentry.init({
  app,
  dsn: config.sentryDsn,
  environment: config.env,
  release: config.release,
  integrations: [Sentry.browserTracingIntegration({ router }), Sentry.replayIntegration({ maskAllText: true })],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.01,
  replaysOnErrorSampleRate: 1.0,
  beforeSend(event) { return scrub(event) },   // удалить чувствительные данные
})
```

SDK захватывает исключение, breadcrumbs (клики, запросы, навигация), stack-trace через source maps и контекст (пользователь, release, браузер).

## Обработка ошибок

```ts
app.config.errorHandler = (err, instance, info) => Sentry.captureException(err, { extra: { info } })
window.addEventListener('unhandledrejection', e => Sentry.captureException(e.reason))
```

- **Error Boundary** через `onErrorCaptured` — показать запасной UI;
- ошибки сети — с кодом и трассой (`traceparent` в заголовках, связка с бэкендом);
- игнорировать шум (расширения браузера, отмена запросов) через `ignoreErrors`.

## Релизы

- release = git sha / версия, загрузка source maps (hidden) при деплое;
- **Release health**: доля сессий без сбоев, регрессии после релиза;
- алерты: рост новой ошибки, падение crash-free rate, ухудшение LCP;
- привязка к коммитам и авторам (suspect commits).

## Приватность

- не логировать токены, пароли, персональные данные;
- маскирование в session replay;
- согласие пользователя и требования законов;
- сэмплирование для снижения объёма и стоимости.

## Метрики продукта

Воронки, конверсия, ошибки на шаге, время выполнения сценариев. Дашборды и SLO: например, 99% загрузок страницы без ошибок.

## Вопросы с ответами

> [!question]- Как связать ошибку фронтенда с бэкендом?
> Передавать trace id (заголовок `traceparent`, OpenTelemetry), логировать его в Sentry и на сервере; по нему находить всю цепочку.

> [!question]- Зачем source maps в Sentry?
> Минифицированный стек читаем только с картами: они показывают исходные файлы и строки. Загружаем в Sentry, но не отдаём публично.
