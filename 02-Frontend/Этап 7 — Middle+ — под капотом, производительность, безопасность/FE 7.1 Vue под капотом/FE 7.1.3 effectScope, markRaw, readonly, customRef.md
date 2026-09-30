---
type: topic
domain: frontend
stage: 7
section: "7.1"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981e1bae2ce04abaf769a
tags: [domain/frontend, stage/7, level/senior, topic/vue, topic/reactivity, topic/advanced, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# effectScope, markRaw, readonly, customRef

↑ [[FE 7.1 Vue под капотом|7.1 Vue под капотом]] · ← [[FE 7.1.2 Scheduler — батчинг обновлений, flush pre-post-sync|Предыдущая]] · → [[FE 7.1.4 Virtual DOM, рендер-функции, компилятор|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Продвинутые API показывают глубину знаний и умение контролировать память и реактивность.

## effectScope

Группирует эффекты, чтобы остановить их одной командой. Основа для composables вне компонентов и для Pinia.

```ts
const scope = effectScope()
scope.run(() => {
  const doubled = computed(() => count.value * 2)
  watch(doubled, () => {})
})
scope.stop()   // остановит computed и watch
```

`onScopeDispose(fn)` — аналог `onUnmounted` для scope; `getCurrentScope()` — текущий scope.

## markRaw и shallow API

```ts
const map = markRaw(new MapboxMap(...))   // никогда не станет реактивным
const state = shallowRef(bigObject)       // реактивна только замена .value
const list = shallowReactive({ items })   // реактивен только первый уровень
```

Использовать для: сторонних экземпляров (карты, графики, Monaco), больших неизменяемых данных (десятки тысяч записей). Триггер вручную: `triggerRef(state)`.

## readonly

```ts
const config = readonly(reactive({ theme: 'dark' }))
config.theme = 'light'   // предупреждение, изменение запрещено
```

Даёт безопасный публичный API стора: наружу отдаём readonly-состояние, меняем через действия.

## customRef

Создание ref с контролем `track` и `trigger`, например debounce:

```ts
function useDebouncedRef<T>(value: T, delay = 300) {
  let timer: number
  return customRef<T>((track, trigger) => ({
    get() { track(); return value },
    set(v) {
      clearTimeout(timer)
      timer = window.setTimeout(() => { value = v; trigger() }, delay)
    },
  }))
}
```

## Вопросы с ответами

> [!question]- Зачем markRaw?
> Чтобы Vue не оборачивал в Proxy экземпляры сторонних библиотек и большие объекты: экономит память и избавляет от багов из-за прокси.

> [!question]- Когда shallowRef лучше ref?
> Когда данные большие и заменяются целиком, а глубокая реактивность не нужна.
