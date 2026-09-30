---
type: topic
domain: frontend
stage: 8
section: "8.4"
order: 4
status: todo
level: senior
notion_id: 3ea33104867981678026ff04289995c0
tags: [domain/frontend, stage/8, level/senior, topic/system-design, topic/realtime, topic/websocket, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Real-time: чат, уведомления

↑ [[FE 8.4 Frontend System Design|8.4 Frontend System Design]] · ← [[FE 8.4.3 Пагинация — offset, cursor, infinite scroll|Предыдущая]] · → [[FE 8.4.5 Офлайн-режим и синхронизация|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Типовой кейс: дизайн чата или уведомлений. Важно выбрать транспорт и продумать надёжность.

## Транспорты

| Способ | Особенности | Когда |
|---|---|---|
| **Polling** | периодические запросы | простое, редкие обновления |
| **Long polling** | запрос висит до события | fallback |
| **SSE** (Server-Sent Events) | односторонний поток от сервера, авто-переподключение | уведомления, лента, прогресс |
| **WebSocket** | двусторонний канал | чат, коллаборация, игры |
| **WebTransport** | на QUIC | продвинутые сценарии |
| **Push** (Web Push) | вне вкладки | важные уведомления |

## Дизайн чата

```text
Client ──WebSocket──▶ Gateway ──▶ Chat service ──▶ DB + Pub/Sub (Redis/Kafka)
```

Клиент:

- состояние соединения: `connecting`, `open`, `reconnecting`, `closed`;
- **переподключение** с экспоненциальной задержкой и jitter;
- **heartbeat** (ping/pong) для обнаружения обрыва;
- **упорядочивание**: серверный `seq` или `timestamp`;
- **доставка**: `clientMsgId` для идемпотентности и дедупликации, статусы «отправляется / доставлено / прочитано»;
- **оффлайн-очередь** отправки, повтор после восстановления;
- **синхронизация после разрыва**: запрос пропущенных сообщений `since=lastSeq`;
- оптимистичное добавление, откат при ошибке;
- индикатор «печатает» с throttle;
- виртуализация списка, подгрузка истории вверх.

```ts
class Socket {
  #ws?: WebSocket; #attempt = 0
  connect() {
    this.#ws = new WebSocket(url)
    this.#ws.onopen = () => { this.#attempt = 0; this.resync() }
    this.#ws.onclose = () => setTimeout(() => this.connect(), Math.min(30_000, 2 ** this.#attempt++ * 1000) + Math.random() * 500)
    this.#ws.onmessage = e => this.handle(JSON.parse(e.data))
  }
}
```

## Уведомления

- SSE или WebSocket для активной вкладки, Web Push для закрытой;
- счётчик непрочитанных и список; синхронизация между вкладками (BroadcastChannel);
- группировка и ограничение частоты;
- разрешение на push — по действию пользователя.

## Масштаб и надёжность

- бэкенд: горизонтальное масштабирование, pub/sub между узлами;
- аутентификация соединения (токен при подключении, обновление);
- лимиты и backpressure;
- деградация: при недоступности WebSocket — polling.

## Вопросы с ответами

> [!question]- SSE или WebSocket?
> SSE — односторонние обновления с сервера, проще, работает через HTTP, авто-переподключение. WebSocket — двусторонний обмен с малой задержкой (чат, совместное редактирование).

> [!question]- Как гарантировать, что сообщения не потеряются при разрыве?
> Серверные порядковые номера, клиент запоминает последний `seq` и после переподключения запрашивает пропущенное; отправка с `clientMsgId` и подтверждения.
