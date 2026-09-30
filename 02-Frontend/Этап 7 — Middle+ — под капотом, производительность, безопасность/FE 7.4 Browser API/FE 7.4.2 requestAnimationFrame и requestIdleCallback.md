---
type: topic
domain: frontend
stage: 7
section: "7.4"
order: 2
status: todo
level: senior
notion_id: 3ea331048679811ab4cec365522782aa
tags: [domain/frontend, stage/7, level/senior, topic/browser-api, topic/raf, topic/scheduling, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# requestAnimationFrame и requestIdleCallback

↑ [[FE 7.4 Browser API|7.4 Browser API]] · ← [[FE 7.4.1 IntersectionObserver, ResizeObserver, MutationObserver|Предыдущая]] · → [[FE 7.4.3 History API и Location|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Планирование работы — ключ к плавности. Спрашивают, чем rAF отличается от setTimeout и когда нужен idle.

## requestAnimationFrame

Колбэк вызывается **перед следующей перерисовкой** (обычно 60 раз в секунду, синхронно с частотой экрана). Останавливается в фоновых вкладках.

```ts
let id = 0
function loop(time: DOMHighResTimeStamp) {
  update(time)
  id = requestAnimationFrame(loop)
}
id = requestAnimationFrame(loop)
// остановка
cancelAnimationFrame(id)
```

Применение: анимации на JS, синхронизация чтений и записей DOM, троттлинг обработчиков `scroll`/`mousemove` до кадра.

```ts
let queued = false
window.addEventListener('scroll', () => {
  if (queued) return
  queued = true
  requestAnimationFrame(() => { render(); queued = false })
})
```

## requestIdleCallback

Колбэк выполняется, когда главный поток свободен. Для несрочных задач.

```ts
requestIdleCallback(deadline => {
  while (deadline.timeRemaining() > 0 && tasks.length) run(tasks.shift()!)
}, { timeout: 2000 })
```

Применение: аналитика, предзагрузка, индексация, разбиение больших вычислений на кусочки. Safari поддерживает не везде: нужен fallback на `setTimeout`.

## Сравнение

| API | Когда срабатывает | Для чего |
|---|---|---|
| `setTimeout` | через N мс (минимум) | отложенное действие |
| `rAF` | перед кадром | визуальные обновления |
| `requestIdleCallback` | в простое | второстепенные задачи |
| `queueMicrotask` | после текущего кода | согласование состояния |
| `scheduler.postTask` | с приоритетом | разбиение работы |
| `scheduler.yield()` | уступить потоку | длинные задачи, INP |

## Вопросы с ответами

> [!question]- Почему анимацию лучше делать на rAF, а не setInterval?
> rAF синхронизирован с частотой обновления экрана, пауза в фоновых вкладках экономит ресурсы, нет пропуска или удвоения кадров.

> [!question]- Как не блокировать интерфейс при большой обработке?
> Разбивать работу на порции и уступать потоку (`scheduler.yield`, `setTimeout`, `requestIdleCallback`), либо вынести в Web Worker.
