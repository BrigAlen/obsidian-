---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 4
status: todo
level: middle
notion_id: 3ea331048679814ea06ec88873e2751d
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/errors, topic/abort, topic/retry, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Обработка ошибок, retry, отмена запросов (AbortController)

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · ← [[FE 5.4.3 Axios — инстансы и интерсепторы|Предыдущая]] · → [[FE 5.4.5 GraphQL — query, mutation, subscription, fragments|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->











> [!info] Зачем это на собесе
> Гонки запросов и устойчивость: отмена устаревших запросов и разумные повторы.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### Отмена

```ts
const ctrl = new AbortController();
fetch(url, { signal: ctrl.signal });        // axios: { signal: ctrl.signal }
ctrl.abort();                                // AbortError

// Поиск: отменять предыдущий запрос при новом вводе
let current: AbortController | null = null;
async function search(q: string) {
  current?.abort(); current = new AbortController();
  try { results.value = await api.get("/search", { params: { q }, signal: current.signal }).then(r => r.data); }
  catch (e) { if (axios.isCancel(e) || (e as Error).name === "AbortError") return; throw e; }
}
onUnmounted(() => current?.abort());
AbortSignal.timeout(5000); AbortSignal.any([userSignal, AbortSignal.timeout(5000)]);
```

Vue Query автоматически передаёт `signal` в `queryFn` и отменяет при смене ключа/размонтировании.

### Повторы (retry)

```ts
async function withRetry<T>(fn: (signal: AbortSignal) => Promise<T>, { attempts = 3, base = 300, signal }: { attempts?: number; base?: number; signal?: AbortSignal } = {}) {
  for (let i = 0; ; i++) {
    try { return await fn(signal!); }
    catch (e) {
      if (i >= attempts - 1 || !isRetryable(e) || signal?.aborted) throw e;
      await sleep(base * 2 ** i + Math.random() * base);          // экспоненциальная задержка с jitter
    }
  }
}
const isRetryable = (e: any) => !e.response || [408, 425, 429, 500, 502, 503, 504].includes(e.response.status);
```

Правила: повторять только идемпотентные запросы и временные ошибки; учитывать `Retry-After`; ограничивать число попыток; не повторять 4xx (кроме 408/429).

### Классификация ошибок и UX

| Ошибка | Реакция |
|---|---|
| Сеть недоступна/timeout | сообщение «нет соединения», кнопка «повторить», офлайн-режим |
| 400/422 | ошибки в полях формы |
| 401 | обновление токена/логин |
| 403 | сообщение о правах |
| 404 | пустое состояние/страница не найдена |
| 409 | конфликт: предложить обновить данные |
| 5xx | общее сообщение + traceId для поддержки |

Глобальная обработка: интерсептор + `onError` Vue Query + `app.config.errorHandler`; отправка в Sentry с контекстом.

## Нюансы и подводные камни

- Гонки: более медленный старый запрос может прийти после нового — отменяйте/сопоставляйте.
- Отмена не откатывает действие на сервере (POST мог выполниться).
- Слепые повторы POST дублируют операции.
- `AbortError` не должен показываться как ошибка пользователю.
- Ретраи при 429 без учёта `Retry-After` усугубляют нагрузку.

## Практика

1. Реализуйте поиск с отменой предыдущего запроса и обработкой `AbortError`.
2. Напишите `withRetry` с jitter и учётом `Retry-After`.
3. Классифицируйте ошибки и покажите различные сообщения.

## Вопросы с ответами

> [!question]- Как отменить запрос?
> `AbortController`: передать `signal` в `fetch`/Axios и вызвать `abort()`.

> [!question]- Какие запросы можно повторять?
> Идемпотентные при временных ошибках (сеть, 5xx, 429), с экспоненциальной задержкой и ограничением попыток.

## Связанные темы

- [[N:3ea331048679812ba856e1ba38a2e798]]
- [[N:3ea33104867981a8a3b1c57d5d9d9535]]
