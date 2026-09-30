---
type: topic
domain: frontend
stage: 7
section: "7.4"
order: 7
status: todo
level: senior
notion_id: 3ea331048679819a931aef1b6e4f88a2
tags: [domain/frontend, stage/7, level/senior, topic/browser-api, topic/workers, topic/threading, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Web Workers

↑ [[FE 7.4 Browser API|7.4 Browser API]] · ← [[FE 7.4.6 BroadcastChannel и postMessage|Предыдущая]] · → [[FE 7.4.8 Canvas и SVG|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Единственный способ настоящей многопоточности в браузере; спрашивают, что можно вынести и как передавать данные.

## Зачем

JavaScript однопоточный: тяжёлое вычисление блокирует UI. Worker выполняет код в отдельном потоке без доступа к DOM.

```ts
// worker.ts
self.onmessage = (e: MessageEvent<number[]>) => {
  const sorted = [...e.data].sort((a, b) => a - b)
  self.postMessage(sorted)
}

// main.ts
const worker = new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' })
worker.postMessage(bigArray)
worker.onmessage = e => { result.value = e.data }
// worker.terminate()
```

## Что переносить

Парсинг больших файлов (CSV, JSON), сортировка и фильтрация больших коллекций, сжатие, шифрование, обработка изображений, WASM-вычисления, markdown/подсветка.

## Передача данных

- **Structured clone** — копирование (дорого для больших данных);
- **Transferable objects** (`ArrayBuffer`) — передача владения без копии: `postMessage(buf, [buf])`;
- `SharedArrayBuffer` + `Atomics` — общая память (требует cross-origin isolation);
- **Comlink** превращает обмен сообщениями в вызовы функций.

```ts
import { wrap } from 'comlink'
const api = wrap<import('./worker').Api>(new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' }))
const result = await api.heavy(data)
```

## Виды воркеров

| Вид | Назначение |
|---|---|
| Dedicated Worker | один владелец |
| Shared Worker | общий для вкладок |
| Service Worker | прокси сети, offline, push |
| Worklet | аудио, отрисовка |

## Нюансы

- нет DOM, `window`, `document`; есть `fetch`, `IndexedDB`, `WebSocket`;
- накладные расходы старта — пул воркеров для частых задач;
- реактивные объекты Vue нельзя передавать (Proxy не клонируется): `toRaw`;
- OffscreenCanvas позволяет рисовать в воркере.

## Вопросы с ответами

> [!question]- Что можно передать без копирования?
> Transferable-объекты (ArrayBuffer, MessagePort, ImageBitmap): владение переходит к воркеру, у отправителя буфер становится пустым.

> [!question]- Почему worker не может менять DOM?
> Он работает в отдельном потоке без доступа к документу; результат отправляется в главный поток, который и обновляет UI.
