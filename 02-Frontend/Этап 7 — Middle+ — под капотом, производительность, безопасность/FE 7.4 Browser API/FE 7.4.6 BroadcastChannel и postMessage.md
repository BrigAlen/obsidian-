---
type: topic
domain: frontend
stage: 7
section: "7.4"
order: 6
status: todo
level: senior
notion_id: 3ea331048679811f8f29c4c3e914a2f1
tags: [domain/frontend, stage/7, level/senior, topic/browser-api, topic/broadcastchannel, topic/postmessage, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# BroadcastChannel и postMessage

↑ [[FE 7.4 Browser API|7.4 Browser API]] · ← [[FE 7.4.5 Clipboard, Notifications, Geolocation|Предыдущая]] · → [[FE 7.4.7 Web Workers|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Коммуникация между вкладками, iframe и окнами: синхронизация выхода, тема, авторизация.

## BroadcastChannel

Сообщения между контекстами одного **origin** (вкладки, iframe, воркеры).

```ts
const bc = new BroadcastChannel('auth')
bc.postMessage({ type: 'logout' })
bc.onmessage = e => { if (e.data.type === 'logout') router.push('/login') }
// bc.close() при размонтировании
```

Применение: единый выход из всех вкладок, синхронизация темы, уведомление об обновлении токена, общий SharedWorker.

## window.postMessage

Связь между **разными** origin: окно, iframe, popup.

```ts
// родитель
iframe.contentWindow!.postMessage({ type: 'init', payload }, 'https://widget.example.com')

// iframe
window.addEventListener('message', e => {
  if (e.origin !== 'https://app.example.com') return   // ОБЯЗАТЕЛЬНО проверять origin
  handle(e.data)
})
```

Безопасность: указывайте точный `targetOrigin` (не `*`) и проверяйте `event.origin` при получении.

## Другие способы

| Способ | Особенности |
|---|---|
| `storage` event | срабатывает в других вкладках при изменении `localStorage` |
| `SharedWorker` | общий воркер для вкладок |
| Service Worker + `clients.postMessage` | рассылка от SW |
| Web Locks API | выбор лидера среди вкладок |
| `MessageChannel` | пара портов для прямой связи |

## Вопросы с ответами

> [!question]- Как синхронизировать logout во всех вкладках?
> Через BroadcastChannel (или `storage` event): при выходе шлём сообщение, остальные вкладки очищают состояние и переходят на страницу входа.

> [!question]- Чем опасен postMessage?
> Без проверки `origin` любой сайт может слать вашему окну данные и команды; с `*` в targetOrigin данные уйдут любому получателю.
