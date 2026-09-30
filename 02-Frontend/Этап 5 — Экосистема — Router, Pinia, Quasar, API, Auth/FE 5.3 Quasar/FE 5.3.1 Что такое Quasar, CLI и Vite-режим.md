---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981319af3fe3805ab8528
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/vue, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Что такое Quasar, CLI и Vite-режим

↑ [[FE 5.3 Quasar|5.3 Quasar]] · → [[FE 5.3.2 Структура проекта и quasar.config|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Quasar — основной UI-фреймворк в стеке; спрашивают, что он даёт кроме набора компонентов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Quasar** — фреймворк на Vue для создания SPA, SSR, PWA, мобильных (Capacitor/Cordova) и десктопных (Electron) приложений **из одной кодовой базы**. Включает: 70+ компонентов Material Design, CLI, сборку (Vite/webpack), утилиты, плагины, CSS-инструменты, i18n-пакеты, иконки.

```bash
npm init quasar                      # создание проекта (Vite-режим, TS, Pinia, Router)
npm run dev                          # quasar dev
quasar build                         # SPA сборка
quasar build -m pwa|ssr|electron|capacitor
quasar mode add ssr                  # добавить режим
```

| Элемент | Что даёт |
|---|---|
| Quasar CLI | `dev`, `build`, режимы, генерация иконок, расширения |
| Vite-режим (`@quasar/app-vite`) | быстрый dev-сервер и сборка Vite (рекомендуется); webpack-режим (`@quasar/app-webpack`) — legacy |
| Tree-shaking | в prod попадают только использованные компоненты (авто-импорт через плагин) |
| Плагины/утилиты | Notify, Dialog, Loading, LocalStorage, Cookies, Dark, Meta |
| Директивы | `v-ripple`, `v-close-popup`, `v-touch-*`, `v-intersection` |
| CSS | flex/grid-классы, типографика, отступы (`q-pa-md`), видимость (`gt-sm`, `lt-md`) |
| Расширения (AE) | готовые модули и генераторы |

Альтернативы: Vuetify (Material, компонентная библиотека), PrimeVue, Element Plus, Naive UI, Nuxt UI. Отличие Quasar: единая кодовая база для web/mobile/desktop и собственный CLI.

Установка вручную в существующий Vite-проект: плагин `@quasar/vite-plugin`, `app.use(Quasar, { plugins: {...} })`.

## Нюансы и подводные камни

- Компонент Quasar подключается автоматически: не нужно ручных импортов, но убедитесь, что включён авто-импорт.
- Версия Quasar v2 работает с Vue 3; v1 — с Vue 2.
- Материал-дизайн по умолчанию: кастомный дизайн требует настройки темы.
- Режимы (SSR/Electron) имеют свои ограничения API.

## Практика

1. Создайте проект Quasar в Vite-режиме с TypeScript и Pinia.
2. Соберите SPA и PWA, сравните вывод.
3. Найдите компонент и плагин из документации для типичной задачи.

## Вопросы с ответами

> [!question]- Что такое Quasar?
> Фреймворк на Vue с UI-компонентами и инструментами сборки для SPA/SSR/PWA/мобильных/десктопных приложений из одной кодовой базы.

> [!question]- Vite-режим или webpack?
> Vite — рекомендуется (быстрее); webpack — для унаследованных проектов.

## Связанные темы

- [[N:3ea331048679818fb89cd4c82a907497]]
- [[N:3ea3310486798162a794f205b40af87d]]
