---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981e4b92aed4daaecffce
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/fetch, topic/axios, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Fetch API и Axios

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · ← [[FE 5.4.1 REST — принципы и соглашения|Предыдущая]] · → [[FE 5.4.3 Axios — инстансы и интерсепторы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Сравнение нативного `fetch` и Axios: что даёт библиотека и когда можно без неё.

## Объяснение

```ts
// fetch
const res = await fetch("/api/orders", {
  method: "POST",
  headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
  body: JSON.stringify(dto),
  credentials: "include", signal: ctrl.signal, cache: "no-store",
});
if (!res.ok) throw new Error(`HTTP ${res.status}`);          // fetch НЕ бросает на 4xx/5xx
const data = await res.json();                                // stream: res.body?.getReader()

// axios
const { data } = await axios.post<Order>("/api/orders", dto, { params: { dryRun: true }, timeout: 10_000, signal: ctrl.signal });
```

| Возможность | `fetch` | Axios |
|---|---|---|
| Исключение при 4xx/5xx | нет | да (`validateStatus`) |
| JSON | вручную `JSON.stringify/res.json()` | автоматически |
| Таймаут | через `AbortSignal.timeout()` | `timeout` |
| Интерсепторы | нет (обёртка) | да |
| Прогресс загрузки/скачивания | стримы | `onUploadProgress/onDownloadProgress` |
| Отмена | `AbortController` | `AbortController` (и устаревший CancelToken) |
| Инстансы и базовые настройки | обёртка | `axios.create` |
| XSRF, сериализация параметров | вручную | из коробки |
| Размер | 0 (нативный) | ~13 КБ |
| Среда | браузер, Node 18+ | браузер, Node |
| Стримы, streaming responses | да | ограниченно (нативно: `adapter: "fetch"`) |

Оба подхода нужно оборачивать в **слой API** (см. [[N:3ea331048679812caa72d90b8bef45f7]]).

Вспомогательное: `URLSearchParams`, `FormData` (загрузка файлов, не задавайте `Content-Type` вручную), `Headers`, `Request/Response`, `AbortSignal.any/timeout`. Альтернативы: `ky`, `ofetch` (`$fetch` Nuxt), `wretch`.

## Нюансы и подводные камни

- Забытая проверка `res.ok` — ошибки проходят незамеченными.
- `res.json()` можно прочитать один раз (клонирование `res.clone()`).
- `fetch` по умолчанию не отправляет cookie на другие origin: `credentials`.
- Таймаута нет по умолчанию у `fetch`.
- `FormData` с заголовком `Content-Type: multipart` вручную ломает `boundary`.

## Практика

1. Напишите обёртку над `fetch` с проверкой статуса, JSON и таймаутом.
2. Реализуйте загрузку файла с прогрессом через Axios.
3. Сравните размер бандла и функциональность.

## Вопросы с ответами

> [!question]- Чем `fetch` отличается от Axios по обработке ошибок?
> `fetch` не бросает исключение на 4xx/5xx (только при сетевой ошибке), Axios бросает по умолчанию.

> [!question]- Как добавить таймаут к `fetch`?
> `AbortSignal.timeout(ms)` или `AbortController` с таймером.

## Связанные темы

- [[N:3ea3310486798111bac4ca5217597700]]
- [[N:3ea331048679812ba856e1ba38a2e798]]
