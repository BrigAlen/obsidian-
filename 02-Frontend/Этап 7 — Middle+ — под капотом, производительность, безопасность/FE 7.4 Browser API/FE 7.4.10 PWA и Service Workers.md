---
type: topic
domain: frontend
stage: 7
section: "7.4"
order: 10
status: todo
level: senior
notion_id: 3ea3310486798159bc13d6758b0e60fa
tags: [domain/frontend, stage/7, level/senior, topic/browser-api, topic/pwa, topic/service-worker, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# PWA и Service Workers

↑ [[FE 7.4 Browser API|7.4 Browser API]] · ← [[FE 7.4.9 Web Components и Shadow DOM|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> PWA даёт offline, установку и push. Спрашивают жизненный цикл SW и стратегии кэша.

## Что такое PWA

Веб-приложение с возможностями нативного: установка на устройство, работа offline, push-уведомления, фоновая синхронизация. Требования: HTTPS, **Web App Manifest**, **Service Worker**.

## Manifest

```json
{
  "name": "Панель заказов",
  "short_name": "Заказы",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1976d2",
  "icons": [
    { "src": "/icons/192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

## Жизненный цикл Service Worker

1. **register** → 2. **install** (кэшируем оболочку) → 3. **waiting** (если открыты вкладки со старой версией) → 4. **activate** (чистим старые кэши) → 5. **control** (перехватывает fetch).

```ts
// регистрация
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
}

// sw.js
const CACHE = 'app-v3'
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(['/', '/offline.html'])))
  self.skipWaiting()
})
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))))
})
self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(hit => hit ?? fetch(e.request).catch(() => caches.match('/offline.html'))))
})
```

## Инструменты

`vite-plugin-pwa` (Workbox): автогенерация SW, стратегии, обновление. Quasar PWA-режим.

## Возможности

- offline-оболочка (App Shell) и offline-данные (IndexedDB);
- **Background Sync**: отправка накопленных запросов при появлении сети;
- **Push API**: уведомления через Service Worker;
- установка: событие `beforeinstallprompt`.

## Подводные камни

- ошибка в SW может «залипнуть» — нужен продуманный процесс обновления (`skipWaiting`, уведомление «есть новая версия»);
- кэш надо версионировать и чистить;
- не кэшировать авторизованные API-ответы без политики;
- iOS: ограниченная поддержка push, отличия в установке;
- отладка: DevTools → Application → Service Workers.

## Вопросы с ответами

> [!question]- Как обновляется Service Worker?
> Браузер проверяет файл sw.js при навигации, новая версия устанавливается и ждёт закрытия вкладок со старой (waiting), либо активируется сразу через `skipWaiting`.

> [!question]- Чем PWA отличается от обычного сайта?
> Manifest и Service Worker дают установку, offline-режим, push и фоновую синхронизацию.
