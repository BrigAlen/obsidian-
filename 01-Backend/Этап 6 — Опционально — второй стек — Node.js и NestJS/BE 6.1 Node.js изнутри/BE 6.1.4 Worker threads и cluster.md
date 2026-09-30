---
type: topic
domain: backend
stage: 6
section: "6.1"
order: 4
status: todo
level: junior
notion_id: 3ea331048679815e88ece14f7c6b80ae
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/concurrency, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Worker threads и cluster

↑ [[BE 6.1 Node.js изнутри|6.1 Node.js изнутри]] · ← [[BE 6.1.3 Streams и Buffer|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

























> [!info] Зачем это на собесе
> Как использовать несколько ядер в Node.js и как выполнять тяжёлые вычисления.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Механизм | Что это | Для чего |
|---|---|---|
| `cluster` | несколько процессов Node.js на одном порту | масштабирование HTTP-сервера по ядрам |
| `worker_threads` | потоки со своим event loop и памятью V8 | CPU-bound вычисления, не блокирующие главный поток |
| `child_process` | запуск внешних процессов | вызов утилит |
| Контейнеры/процесс-менеджеры (PM2, Kubernetes) | несколько реплик | предпочтительный способ масштабирования |

```js
// main.js
import { Worker } from "node:worker_threads";
const run = (n) => new Promise((resolve, reject) => {
  const w = new Worker(new URL("./fib.js", import.meta.url), { workerData: n });
  w.once("message", resolve); w.once("error", reject);
});
console.log(await run(42));

// fib.js
import { parentPort, workerData } from "node:worker_threads";
const fib = (n) => (n < 2 ? n : fib(n - 1) + fib(n - 2));
parentPort.postMessage(fib(workerData));
```

Данные между потоками копируются (structured clone), либо передаются без копирования через `transfer` и `SharedArrayBuffer` + `Atomics`.

## Нюансы и подводные камни

- Создание воркера дорого: используйте пул (Piscina).
- Worker threads не ускоряют I/O-bound задачи.
- Общее состояние приложения в cluster не разделяется: сессии и кэш храните во внешнем хранилище.
- Состояние гонки возможно только при `SharedArrayBuffer`.
- В контейнерах обычно проще запускать по одному процессу на контейнер и масштабировать репликами.

## Практика

1. Вынесите тяжёлое вычисление в worker и сравните задержку API.
2. Настройте пул воркеров через Piscina.
3. Запустите приложение в cluster и проверьте распределение запросов.

## Вопросы с ответами

> [!question]- Cluster или worker threads?
> Cluster — несколько процессов для масштабирования сервера; worker threads — потоки для тяжёлых вычислений внутри процесса.

> [!question]- Помогут ли worker threads при медленной БД?
> Нет: это I/O-bound, помогает асинхронность.

## Связанные темы

- [[N:3ea3310486798147ba50e9e03c350889]]
- [[N:3ea33104867981c0b1f6cbbaf8a20394]]
