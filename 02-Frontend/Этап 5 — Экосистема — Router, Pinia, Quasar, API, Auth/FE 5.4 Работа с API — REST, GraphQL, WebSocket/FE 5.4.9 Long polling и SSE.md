---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 9
status: todo
level: middle
notion_id: 3ea3310486798173bebcd71df11c13c6
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/sse, topic/realtime, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Long polling и SSE

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · ← [[FE 5.4.8 WebSocket|Предыдущая]] · → [[FE 5.4.10 Слой API в приложении — сервисы и типизация|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



















> [!info] Зачем это на собесе
> Более простые альтернативы WebSocket для односторонних обновлений.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Технология | Как работает | Направление | Особенности |
|---|---|---|---|
| Short polling | запрос по таймеру | клиент → сервер | просто, лишняя нагрузка и задержка |
| Long polling | запрос висит, пока не появятся данные или таймаут, затем сразу новый | клиент → сервер | работает везде; нагрузка на соединения |
| **SSE** (Server-Sent Events) | постоянное HTTP-соединение, сервер шлёт `text/event-stream` | сервер → клиент | авто-переподключение, `Last-Event-ID`, только текст, HTTP/2 мультиплексирование |
| WebSocket | двусторонний канал | оба | бинарные данные, свой протокол |

```ts
// SSE
const es = new EventSource("/api/orders/stream", { withCredentials: true });
es.addEventListener("order-updated", (e) => handle(JSON.parse((e as MessageEvent).data)));
es.onerror = () => { /* браузер сам переподключается; es.readyState */ };
es.close();
```

```text
Формат потока:
id: 42
event: order-updated
data: {"id":1,"status":"paid"}
retry: 5000
```

Ограничения EventSource: только GET, нельзя задать заголовки (аутентификация через cookie/query), ограничение ~6 соединений на домен в HTTP/1.1. Для POST/заголовков — `fetch` + чтение потока (`@microsoft/fetch-event-source`).

```ts
// Long polling
async function poll(signal: AbortSignal, since = 0) {
  while (!signal.aborted) {
    try { const r = await fetch(`/api/events?since=${since}`, { signal }); if (r.status === 200) { const { events, cursor } = await r.json(); events.forEach(handle); since = cursor; } }
    catch { await sleep(2000); }          // backoff при ошибке
  }
}
```

Выбор: уведомления, прогресс задач, ленты — SSE; чат, игры, совместное редактирование — WebSocket; окружение без поддержки — long polling. Через прокси убедитесь, что не буферизуется ответ (`X-Accel-Buffering: no`).

## Нюансы и подводные камни

- Прокси/CDN могут буферизовать SSE и ломать поток.
- Потерянные события: используйте `id` и `Last-Event-ID` для догоняющей отправки.
- Закрывайте `EventSource` при размонтировании.
- Много вкладок × много соединений — лимиты.
- Безопасность: авторизация по cookie и проверка origin.

## Практика

1. Реализуйте прогресс фоновой задачи через SSE.
2. Сравните нагрузку short polling, long polling и SSE.
3. Добавьте `Last-Event-ID` и повторное подключение.

## Вопросы с ответами

> [!question]- SSE или WebSocket?
> SSE — односторонний поток от сервера, проще и с авто-переподключением; WebSocket — двусторонний обмен, бинарные данные.

> [!question]- Как работает long polling?
> Клиент отправляет запрос, сервер держит его до появления данных или таймаута, после ответа клиент сразу отправляет новый.

## Связанные темы

- [[N:3ea33104867981cebb9ce4aaf0305137]]
- [[N:3ea331048679812caa72d90b8bef45f7]]
