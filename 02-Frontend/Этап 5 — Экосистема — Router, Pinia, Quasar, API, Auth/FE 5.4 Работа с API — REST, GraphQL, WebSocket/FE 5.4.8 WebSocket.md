---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 8
status: todo
level: middle
notion_id: 3ea33104867981cebb9ce4aaf0305137
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/websocket, topic/realtime, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# WebSocket

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · ← [[FE 5.4.7 graphql-codegen и graphql-request|Предыдущая]] · → [[FE 5.4.9 Long polling и SSE|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















> [!info] Зачем это на собесе
> Двусторонний реалтайм: соединение, переподключение, аутентификация и обработка отсутствия сети.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

WebSocket — постоянное двустороннее соединение поверх TCP (апгрейд HTTP): низкая задержка, сообщения в обе стороны, без накладных заголовков.

```ts
const ws = new WebSocket("wss://api.example.com/ws?ticket=" + ticket);
ws.onopen = () => ws.send(JSON.stringify({ type: "subscribe", topic: "orders" }));
ws.onmessage = (e) => handle(JSON.parse(e.data));
ws.onerror = (e) => console.error(e);
ws.onclose = (e) => scheduleReconnect(e.code);
ws.close(1000, "bye");
// ws.readyState: CONNECTING 0, OPEN 1, CLOSING 2, CLOSED 3; binaryType: "blob" | "arraybuffer"
```

Надёжный клиент (composable):

```ts
export function useSocket(url: MaybeRefOrGetter<string>) {
  const status = ref<"connecting" | "open" | "closed">("closed"); let ws: WebSocket | undefined, attempt = 0, timer: number;
  const queue: string[] = [];
  function connect() {
    status.value = "connecting"; ws = new WebSocket(toValue(url));
    ws.onopen = () => { attempt = 0; status.value = "open"; queue.splice(0).forEach(m => ws!.send(m)); startHeartbeat(); };
    ws.onmessage = (e) => emit("message", JSON.parse(e.data));
    ws.onclose = () => { status.value = "closed"; stopHeartbeat(); timer = window.setTimeout(connect, Math.min(30_000, 500 * 2 ** attempt++) + Math.random() * 500); };   // backoff + jitter
  }
  const send = (m: unknown) => { const s = JSON.stringify(m); ws?.readyState === 1 ? ws.send(s) : queue.push(s); };
  onScopeDispose(() => { clearTimeout(timer); ws?.close(); });
  connect();
  return { status, send };
}
```

Практики:

| Тема | Решение |
|---|---|
| Аутентификация | браузерный WebSocket не позволяет заголовки: одноразовый ticket в query/`Sec-WebSocket-Protocol` или cookie; токен в query логируется — избегайте долгоживущих |
| Переподключение | экспоненциальная задержка с jitter, повторная подписка |
| Heartbeat (ping/pong) | обнаружение «мёртвых» соединений, keep-alive через прокси |
| Протокол сообщений | типы, версии, идентификаторы, подтверждения (ack) |
| Пропущенные события | при переподключении — запросить состояние/`lastEventId` |
| Онлайн/офлайн | `navigator.onLine`, события `online/offline` |
| Библиотеки | `socket.io` (комнаты, fallback), `@microsoft/signalr`, `reconnecting-websocket`, VueUse `useWebSocket` |
| Масштабирование | sticky sessions/backplane на сервере |

Интеграция с Vue Query: по сообщению `qc.setQueryData/invalidateQueries`, а не отдельное состояние.

## Нюансы и подводные камни

- Прокси/балансировщики закрывают простаивающие соединения — heartbeat и настройка таймаутов.
- Сообщения не гарантируют доставку и порядок при разрывах: делайте идемпотентную обработку.
- Утечки: закрывайте сокет при размонтировании.
- Вкладки в фоне: браузер может замедлять таймеры.
- Открытый сокет на каждой вкладке — нагрузка: `BroadcastChannel`/`SharedWorker`.

## Практика

1. Реализуйте `useSocket` с переподключением и heartbeat.
2. Обновляйте кэш Vue Query по сообщениям сервера.
3. Разберитесь с аутентификацией сокета через ticket.

## Вопросы с ответами

> [!question]- Чем WebSocket отличается от HTTP polling?
> Постоянное двустороннее соединение с низкой задержкой вместо повторяющихся запросов.

> [!question]- Как аутентифицировать WebSocket в браузере?
> Через cookie либо короткоживущий ticket в URL/подпротоколе, так как заголовки задать нельзя.

## Связанные темы

- [[N:3ea331048679818eacacea12f103344c]]
- [[N:3ea3310486798173bebcd71df11c13c6]]
