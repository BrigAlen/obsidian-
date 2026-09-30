---
type: topic
domain: frontend
stage: 8
section: "8.1"
order: 6
status: todo
level: senior
notion_id: 3ea33104867981f9867dd44b67b8c411
tags: [domain/frontend, stage/8, level/senior, topic/rxjs, topic/reactive, topic/streams, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Реактивное программирование и RxJS (обзорно)

↑ [[FE 8.1 Парадигмы — ООП, ФП, SOLID|8.1 Парадигмы: ООП, ФП, SOLID]] · ← [[FE 8.1.5 Декларативный и императивный подход|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Достаточно понимать идею потоков, ключевые операторы и отличие от Promise; RxJS часто встречается в Angular и сложных сценариях.

## Идея

Данные — **потоки событий во времени**. Подписываемся и реагируем, комбинируя потоки операторами.

## Observable vs Promise

| | Promise | Observable |
|---|---|---|
| Значений | одно | ноль, одно или много |
| Выполнение | сразу (eager) | ленивое, при подписке |
| Отмена | нет (AbortController) | `unsubscribe()` |
| Операторы | `then/catch` | десятки (`map`, `switchMap`, `debounceTime`) |

## Пример: поиск

```ts
import { fromEvent, debounceTime, map, distinctUntilChanged, switchMap, catchError, of } from 'rxjs'
import { ajax } from 'rxjs/ajax'

const sub = fromEvent<InputEvent>(input, 'input').pipe(
  map(e => (e.target as HTMLInputElement).value.trim()),
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(q => ajax.getJSON(`/api/search?q=${q}`).pipe(catchError(() => of([])))),
).subscribe(render)

// sub.unsubscribe() при размонтировании
```

`switchMap` отменяет предыдущий запрос при новом значении — решает гонки запросов.

## Основные операторы

| Категория | Операторы |
|---|---|
| Преобразование | `map`, `scan`, `pluck` |
| Фильтрация | `filter`, `take`, `debounceTime`, `distinctUntilChanged` |
| Комбинирование | `combineLatest`, `merge`, `zip`, `withLatestFrom` |
| Высшего порядка | `switchMap`, `mergeMap`, `concatMap`, `exhaustMap` |
| Ошибки | `catchError`, `retry` |

Выбор: `switchMap` — только последнее (поиск), `concatMap` — по очереди, `mergeMap` — параллельно, `exhaustMap` — игнорировать, пока идёт (кнопка «отправить»).

## Subjects и Hot/Cold

- `Subject`, `BehaviorSubject` (хранит текущее значение), `ReplaySubject`;
- **cold**: каждый подписчик запускает своё выполнение (HTTP);
- **hot**: общий источник (события), `share()`, `shareReplay(1)`.

## Во Vue

Vue использует свои refs. Для RxJS: `@vueuse/rxjs` (`useObservable`, `useSubscription`), либо `watch` + `debounce` + `AbortController` для простых задач.

## Утечки

Всегда отписывайтесь (`takeUntil`, `unsubscribe`, `takeUntilDestroyed`). Незавершённые подписки — классическая утечка.

## Вопросы с ответами

> [!question]- Когда RxJS оправдан, а когда хватит Promise?
> Для сложных потоков: автоподстановка, комбинирование источников, WebSocket, отмена, повтор. Для одиночного запроса достаточно `fetch` и `async/await`.

> [!question]- Разница между switchMap и mergeMap?
> `switchMap` отменяет предыдущий внутренний поток при новом значении, `mergeMap` запускает все параллельно.
