---
type: topic
domain: frontend
stage: 9
section: "9.2"
order: 5
status: todo
level: senior
notion_id: 32db5d52a6274d47a51b3d9be0f24b81
tags: [domain/frontend, stage/9, level/senior, topic/interview, topic/live-coding, topic/javascript, topic/vue, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Live coding: JavaScript, TypeScript и Vue 3

↑ [[FE 9.2 Финальная подготовка — live coding и вопросы|9.2 Финальная подготовка: live coding и вопросы]] · ← [[FE 9.2.4 Вопросы по тестированию на собесе|Предыдущая]] · → [[FE 9.2.6 Mock-интервью по Frontend System Design|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Задачи на 30–60 минут: оценивают не только результат, но и процесс, чтение требований и общение.

## Как вести себя

1. **Уточните** условие, форматы, ограничения, примеры.
2. **Проговаривайте** ход мысли.
3. **Начните с простого** рабочего решения, затем улучшайте.
4. **Тестируйте** на примерах и граничных случаях.
5. Назовите **сложность**.
6. **Не молчите** в тупике: скажите, что пробуете и почему.

## Типовые задачи JavaScript

```ts
// 1. debounce
const debounce = <A extends unknown[]>(fn: (...a: A) => void, ms: number) => {
  let t: ReturnType<typeof setTimeout>
  return (...a: A) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms) }
}

// 2. Promise.all / Promise.race / retry
async function retry<T>(fn: () => Promise<T>, times = 3, delay = 200): Promise<T> {
  try { return await fn() }
  catch (e) {
    if (times <= 1) throw e
    await new Promise(r => setTimeout(r, delay))
    return retry(fn, times - 1, delay * 2)
  }
}

// 3. пул параллельных запросов
async function pool<T>(tasks: (() => Promise<T>)[], limit: number) {
  const res: T[] = []; let i = 0
  const worker = async () => { while (i < tasks.length) { const k = i++; res[k] = await tasks[k]() } }
  await Promise.all(Array.from({ length: limit }, worker))
  return res
}

// 4. deepEqual, deepClone, flatten, groupBy, memoize, curry, bind
// 5. EventEmitter, LRU-кэш, очередь задач
```

## Задачи TypeScript

```ts
// типы-утилиты своими руками
type MyPick<T, K extends keyof T> = { [P in K]: T[P] }
type MyReadonly<T> = { readonly [P in keyof T]: T[P] }
type DeepPartial<T> = { [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K] }
type ElementType<T> = T extends (infer U)[] ? U : never
type Awaited2<T> = T extends Promise<infer U> ? Awaited2<U> : T

// типизация функции с дженериками
function groupBy<T, K extends PropertyKey>(items: T[], key: (i: T) => K): Record<K, T[]> {
  return items.reduce((acc, i) => { (acc[key(i)] ||= []).push(i); return acc }, {} as Record<K, T[]>)
}
```

## Задачи Vue 3

| Задача | Что проверяют |
|---|---|
| Todo-список | `ref`, `v-for`, `v-model`, события |
| Счётчик, таймер | реактивность, очистка эффектов |
| Автокомплит | debounce, отмена запроса, `watch` |
| Таблица с сортировкой и фильтром | `computed`, ключи, производительность |
| Модальное окно | `Teleport`, `slot`, фокус, `v-model` |
| Форма с валидацией | реактивная валидация, ошибки, `defineEmits` |
| Бесконечная прокрутка | `IntersectionObserver`, composable |
| Star rating, аккордеон, tabs | компоненты и доступность |
| Composable `useFetch`, `useDebounce`, `useLocalStorage` | абстракции, типы |

```vue
<script setup lang="ts">
const q = ref('')
const items = ref<string[]>([])
let ctrl: AbortController | undefined

watchDebounced(q, async (v) => {
  ctrl?.abort(); ctrl = new AbortController()
  if (v.length < 2) return void (items.value = [])
  items.value = await fetch(`/api/suggest?q=${encodeURIComponent(v)}`, { signal: ctrl.signal }).then(r => r.json())
}, { debounce: 300 })
</script>
```

## Что смотрят

- корректность и граничные случаи;
- чистота кода, именование, декомпозиция;
- знание платформы (event loop, замыкания, `this`, промисы);
- доступность и UX;
- работа с ошибками, загрузкой, отменой;
- оценка сложности;
- общение и реакция на подсказки.

## Тренировка

- решайте на время (30–45 минут) вслух;
- используйте платформы (LeetCode, Codewars, GreatFrontEnd);
- тренируйте написание кода без автодополнения;
- разберите ошибки после каждой попытки.

## Вопросы с ответами

> [!question]- Что делать, если завис на задаче?
> Проговорить, что понятно и что нет, упростить (решить частный случай), нарисовать пример, спросить уточнение. Молчание — худшая стратегия.

> [!question]- Что важнее: рабочий код или идеальный?
> Сначала рабочее решение и проверка, затем улучшения и обсуждение компромиссов; идеальное, но нерабочее — провал.
