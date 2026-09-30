---
type: topic
domain: backend
stage: 6
section: "6.1"
order: 1
status: todo
level: junior
notion_id: 3ea33104867981eca57edd25122e2f4d
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/event-loop, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Event loop в Node.js и libuv

↑ [[BE 6.1 Node.js изнутри|6.1 Node.js изнутри]] · → [[BE 6.1.2 Модули, npm, package.json|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Главный вопрос по Node.js: почему один поток обслуживает тысячи запросов и что блокирует event loop.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Node.js выполняет JavaScript в **одном главном потоке**. Ввод-вывод делегируется операционной системе и пулу потоков **libuv**, а результат возвращается в главный поток через очереди событий.

Фазы цикла (упрощённо):

| Фаза | Что выполняется |
|---|---|
| timers | колбэки `setTimeout`, `setInterval` |
| pending callbacks | отложенные системные колбэки |
| poll | новые события ввода-вывода, выполнение их колбэков |
| check | колбэки `setImmediate` |
| close callbacks | закрытие сокетов и дескрипторов |

Между колбэками выполняются **микрозадачи**: сначала `process.nextTick`, затем очередь промисов (`then`, `await`).

```js
console.log("1 sync");
setTimeout(() => console.log("4 timeout"), 0);
setImmediate(() => console.log("5 immediate"));
Promise.resolve().then(() => console.log("3 promise"));
process.nextTick(() => console.log("2 nextTick"));
// порядок: 1, 2, 3, затем 4/5 (порядок timeout и immediate в главном модуле не гарантирован)
```

Пул потоков libuv (по умолчанию 4, `UV_THREADPOOL_SIZE`) обслуживает операции без асинхронного API в ОС: файловая система, DNS-lookup, часть криптографии, zlib. Сетевой ввод-вывод идёт через epoll/kqueue/IOCP без потоков.

## Нюансы и подводные камни

- Тяжёлое вычисление в JS-коде блокирует весь процесс: все запросы ждут (`JSON.parse` огромного тела, `crypto.pbkdf2Sync`, цикл на миллиард итераций).
- Синхронные API (`fs.readFileSync`) допустимы только при старте.
- Бесконечная рекурсия `process.nextTick` «голодит» ввод-вывод.
- Node.js масштабируют процессами (cluster, контейнеры) и worker threads (см. [[N:3ea331048679815e88ece14f7c6b80ae]]).
- Нагрузка измеряется задержкой event loop (`perf_hooks.monitorEventLoopDelay`).

## Практика

1. Заблокируйте event loop циклом и измерьте задержку ответа другого эндпоинта.
2. Предскажите порядок вывода для смеси `setTimeout`, `setImmediate`, промисов и `nextTick`.
3. Замерьте влияние `UV_THREADPOOL_SIZE` на параллельное хэширование.

## Вопросы с ответами

> [!question]- Как Node.js обслуживает много соединений одним потоком?
> Неблокирующий ввод-вывод: запросы регистрируются в ОС, а event loop выполняет колбэки по готовности событий.

> [!question]- Чем nextTick отличается от промисов?
> `nextTick` выполняется раньше очереди промисов, сразу после текущей операции.

> [!question]- Что блокирует event loop?
> Долгий синхронный код в главном потоке.

## Связанные темы

- [[N:3ea33104867981099ac9ff396547152a]]
- [[N:3ea331048679815e88ece14f7c6b80ae]]
