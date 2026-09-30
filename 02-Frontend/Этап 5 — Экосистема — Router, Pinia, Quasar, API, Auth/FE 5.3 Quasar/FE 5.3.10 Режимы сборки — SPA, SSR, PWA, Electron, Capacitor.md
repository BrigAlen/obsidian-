---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 10
status: todo
level: middle
notion_id: 3ea331048679811593a2ee4be38da7e1
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/build, topic/pwa, topic/ssr, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Режимы сборки: SPA, SSR, PWA, Electron, Capacitor

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.9 Темизация — SASS-переменные, brand colors, dark mode|Предыдущая]] · → [[FE 5.3.11 i18n|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> Ключевое преимущество Quasar — единая кодовая база для разных платформ; нужно знать ограничения каждого режима.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Режим | Результат | Особенности |
|---|---|---|
| **SPA** | статические файлы | простой деплой на CDN/nginx; SEO ограничено |
| **SSR** | Node-сервер, HTML на сервере | SEO, быстрый первый показ; нужно оберегать код от использования `window` на сервере, гидратация, `preFetch` |
| **PWA** | SPA + Service Worker + manifest | офлайн, установка, push; Workbox (`GenerateSW`/`InjectManifest`), стратегии кэша |
| **Electron** | десктоп (Windows/macOS/Linux) | доступ к Node/ОС, main/preload-процессы, безопасность (contextIsolation, IPC) |
| **Capacitor** (или Cordova) | мобильное приложение (iOS/Android) | нативные плагины (камера, файлы, push), сборка в Xcode/Android Studio |
| **BEX** | браузерное расширение | manifest v3 |

```bash
quasar mode add pwa && quasar build -m pwa
quasar mode add capacitor && quasar dev -m capacitor -T android
quasar build -m electron
```

Общие практики:

- Платформенно-зависимый код скрыт за адаптерами/фичефлагами (`$q.platform.is.capacitor`), проверка `process.env.MODE`, `process.env.CLIENT`.
- Конфигурация окружения отдельно на режим (`build.env`).
- PWA: стратегии кэширования (Cache First для ассетов, Network First для API), обновление приложения (`skipWaiting` + уведомление), офлайн-страница, HTTPS.
- SSR: без `window/document` на сервере; хранилища — на запрос (Pinia), данные — `preFetch`; кэширование страниц.
- Electron/Capacitor: безопасность (не отключать `contextIsolation`, минимальные IPC), подпись и обновление приложений.

Выбор: внутренние корпоративные системы — обычно SPA (и PWA при необходимости), публичные страницы с SEO — SSR или prerender, мобильные — Capacitor.

## Нюансы и подводные камни

- Service Worker кэширует агрессивно: пользователи «застревают» на старой версии без стратегии обновления.
- SSR увеличивает сложность деплоя и мониторинга (Node-процесс).
- Мобильные режимы требуют нативных SDK и подписи; веб-API отличаются.
- Не все библиотеки поддерживают SSR/Electron.

## Практика

1. Добавьте режим PWA и проверьте офлайн-работу и установку.
2. Соберите SPA и SSR и сравните первый показ.
3. Опишите, какие платформенные различия вы изолируете адаптерами.

## Вопросы с ответами

> [!question]- Зачем несколько режимов сборки в Quasar?
> Один код для web, PWA, SSR, десктопа и мобильных платформ.

> [!question]- Основная проблема PWA?
> Обновление: Service Worker кэширует ресурсы, и без правильной стратегии пользователи не получают новую версию.

## Связанные темы

- [[N:3ea33104867981ccb8a9f3af56b3a9be]]
- [[N:3ea331048679814bbe6ef6cd309478ce]]
