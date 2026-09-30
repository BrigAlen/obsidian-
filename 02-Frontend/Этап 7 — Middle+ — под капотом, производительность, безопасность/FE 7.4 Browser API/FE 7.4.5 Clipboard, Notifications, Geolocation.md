---
type: topic
domain: frontend
stage: 7
section: "7.4"
order: 5
status: todo
level: senior
notion_id: 3ea33104867981958c3bd5d6f335cf69
tags: [domain/frontend, stage/7, level/senior, topic/browser-api, topic/clipboard, topic/notifications, topic/geolocation, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Clipboard, Notifications, Geolocation

↑ [[FE 7.4 Browser API|7.4 Browser API]] · ← [[FE 7.4.4 File API, Blob, FileReader, загрузка файлов|Предыдущая]] · → [[FE 7.4.6 BroadcastChannel и postMessage|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Общие принципы: асинхронность, разрешения, безопасный контекст. Спрашивают, как обрабатывать отказ.

## Общие правила

- требуется **HTTPS** (secure context);
- запрос разрешения только по **действию пользователя**;
- разрешение можно отозвать, всегда обрабатывайте отказ и недоступность;
- статус: `navigator.permissions.query({ name: 'geolocation' })`.

## Clipboard

```ts
await navigator.clipboard.writeText('текст')
const text = await navigator.clipboard.readText()   // запрашивает разрешение

await navigator.clipboard.write([
  new ClipboardItem({ 'image/png': blob }),
])
```

Fallback для старых браузеров — `document.execCommand('copy')` (устарел).

## Notifications

```ts
if ('Notification' in window) {
  const perm = await Notification.requestPermission()   // granted / denied / default
  if (perm === 'granted') new Notification('Новый заказ', { body: '№ 1024', tag: 'order' })
}
```

Для push при закрытой вкладке: Service Worker + Push API (`registration.showNotification`, подписка через VAPID-ключи).

## Geolocation

```ts
navigator.geolocation.getCurrentPosition(
  pos => setPoint(pos.coords.latitude, pos.coords.longitude),
  err => { if (err.code === err.PERMISSION_DENIED) showManualInput() },
  { enableHighAccuracy: false, timeout: 5000, maximumAge: 60_000 },
)
const watchId = navigator.geolocation.watchPosition(cb)
navigator.geolocation.clearWatch(watchId)
```

## Практика

- объяснить пользователю, зачем разрешение, прежде чем его запрашивать;
- предусмотреть ручной ввод как альтернативу;
- приватность: не хранить координаты без необходимости.

## Вопросы с ответами

> [!question]- Почему navigator.clipboard не работает по http?
> Это API secure context: доступен только по HTTPS (и localhost).

> [!question]- Когда запрашивать разрешение на уведомления?
> В ответ на действие пользователя и в понятном контексте («Уведомлять о новых заказах?»), а не при загрузке страницы.
