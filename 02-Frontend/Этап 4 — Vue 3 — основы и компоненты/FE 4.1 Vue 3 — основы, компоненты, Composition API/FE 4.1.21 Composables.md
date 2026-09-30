---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 21
status: todo
level: middle
notion_id: 3ea33104867981c78367f30abc89391d
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/composables, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Composables

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.20 Асинхронные компоненты и lazy loading|Предыдущая]] · → [[FE 4.1.22 VueUse|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Composables — способ переиспользования логики; смотрят на именование, реактивные аргументы и очистку.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Composable** — функция с префиксом `use`, инкапсулирующая **состояние и логику с реактивностью** (вызывается в `setup`).

```ts
// useFetch.ts
export function useFetch<T>(url: MaybeRefOrGetter<string>) {
  const data = shallowRef<T | null>(null);
  const error = ref<Error | null>(null);
  const loading = ref(false);
  let ctrl: AbortController | undefined;

  async function run() {
    ctrl?.abort(); ctrl = new AbortController();
    loading.value = true; error.value = null;
    try {
      const res = await fetch(toValue(url), { signal: ctrl.signal });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      data.value = await res.json();
    } catch (e) { if ((e as Error).name !== "AbortError") error.value = e as Error; }
    finally { loading.value = false; }
  }

  watchEffect(run);                                     // повторный запрос при смене url
  onScopeDispose(() => ctrl?.abort());                  // очистка при уничтожении области
  return { data, error, loading, refresh: run };
}

// Использование
const { data: orders, loading } = useFetch<Order[]>(() => `/api/orders?page=${page.value}`);
```

Соглашения:

- Имя `useXxx`; файл `useXxx.ts`.
- **Входные параметры**: принимайте `MaybeRefOrGetter` и читайте через `toValue` — реактивные и обычные значения работают одинаково.
- **Возвращаемое значение**: объект `refs` (легко деструктурируется без потери реактивности).
- **Побочные эффекты и очистка**: `onScopeDispose`/`onUnmounted`, `watch` с `onCleanup`.
- **Состояние**: локальное (создаётся при каждом вызове) или общее (модульная область — синглтон; для общего лучше Pinia).
- Не принимайте компонентный контекст неявно; хуки жизненного цикла требуют вызова в `setup`.

Примеры: `useToggle`, `useDebounce`, `usePagination`, `useForm`, `useAuth`, `useMediaQuery`, `useInfiniteScroll`.

Composables vs альтернативы:

| Подход | Проблема / особенность |
|---|---|
| Миксины | неявные источники, конфликты имён |
| Renderless-компоненты | лишний слой компонентов |
| Утилиты | без реактивности |
| Pinia | глобальное состояние и DevTools |

## Нюансы и подводные камни

- Composable с хуками, вызванный вне `setup`/асинхронно после `await`, теряет контекст.
- Синглтон-состояние в модуле — проблема для SSR (общее между запросами).
- Не возвращайте `reactive`-объект, который придётся деструктурировать.
- Тестируйте composables как обычные функции (`withSetup` хелпер, `mount` обёртка).

## Практика

1. Напишите `useDebouncedRef`, `usePagination`, `useLocalStorage`.
2. Сделайте `useFetch` с отменой и повторными запросами.
3. Протестируйте composable с фейковыми таймерами.

## Вопросы с ответами

> [!question]- Что такое composable?
> Функция, инкапсулирующая реактивную логику и состояние для повторного использования, по соглашению начинающаяся с `use`.

> [!question]- Как принять аргумент и реактивным, и обычным?
> Использовать `MaybeRefOrGetter<T>` и читать через `toValue`.

## Связанные темы

- [[N:3ea33104867981fcb497fa1eaf2daa2e]]
- [[N:3ea33104867981b2a2b2e2ba946e571c]]
