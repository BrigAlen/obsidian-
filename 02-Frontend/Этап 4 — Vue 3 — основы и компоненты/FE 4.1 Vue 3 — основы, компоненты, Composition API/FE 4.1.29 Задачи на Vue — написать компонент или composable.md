---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 29
status: todo
level: middle
notion_id: 3ea33104867981169f15c64990328a32
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/interview, topic/live-coding, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Задачи на Vue: написать компонент или composable

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.28 Testing Library для Vue — тесты с позиции пользователя|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





















> [!info] Зачем это на собесе
> Live coding на Vue: обычно небольшой компонент или composable за 30–40 минут.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Задачи

**1. Компонент «Счётчик» с `v-model`, min/max и шагом.**

> [!question]- Решение
> ```vue
> \<script setup lang="ts">
> const props = withDefaults(defineProps<{ min?: number; max?: number; step?: number }>(), { min: 0, max: Infinity, step: 1 });
> const model = defineModel\<number>({ default: 0 });
> const inc = () => (model.value = Math.min(props.max, model.value + props.step));
> const dec = () => (model.value = Math.max(props.min, model.value - props.step));
> </script>
> \<template\>
>   <div role="group" aria-label="Количество">
>     \<button type="button" :disabled="model <= min" @click="dec" aria-label="Меньше">−</button\>
>     \<output>{{ model }}</output\>
>     \<button type="button" :disabled="model >= max" @click="inc" aria-label="Больше">+</button\>
>   </div>
> </template>
> ```

**2. Composable `useDebouncedRef(value, delay)`.**

> [!question]- Решение
> ```ts
> export function useDebouncedRef\<T>(value: T, delay = 300) {
>   let timer: ReturnType\<typeof setTimeout>;
>   return customRef\<T>((track, trigger) => ({
>     get() { track(); return value; },
>     set(v) { clearTimeout(timer); timer = setTimeout(() => { value = v; trigger(); }, delay); },
>   }));
> }
> ```

**3. Поиск с подсказками: debounce, отмена запроса, состояния loading/error/empty.**

> [!question]- Что оценивают
> Debounce ввода, `AbortController` (гонки), обработку ошибок, `key` в списке, доступность (`role="listbox"`, стрелки, Enter), очистку при размонтировании.

**4. Бесконечный список: подгрузка при прокрутке.**

> [!question]- Решение
> Sentinel-элемент + `useIntersectionObserver`; защита от повторных запросов (`loading`, `hasMore`); сохранение позиции прокрутки; отмена при размонтировании.

**5. Вкладки (`Tabs`/`Tab`) через `provide/inject` или `component :is`, клавиатурная навигация.**

**6. Модальное окно: Teleport, focus trap, закрытие по Esc и клику вне, блокировка прокрутки, `aria-modal`.**

**7. Реализуйте `useLocalStorage(key, default)` с синхронизацией между вкладками.**

> [!question]- Решение
> ```ts
> export function useLocalStorage\<T>(key: string, def: T) {
>   const read = () => { try { const v = localStorage.getItem(key); return v ? (JSON.parse(v) as T) : def; } catch { return def; } };
>   const state = ref(read()) as Ref\<T>;
>   watch(state, (v) => localStorage.setItem(key, JSON.stringify(v)), { deep: true });
>   useEventListener(window, "storage", (e: StorageEvent) => { if (e.key === key) state.value = read(); });
>   return state;
> }
> ```

**8. Найдите ошибки в коде.**

```vue
<script setup>
const { user } = useUser();          // user — не реактивен, если composable вернул reactive
const list = reactive([]);
async function load() { list = await api.list(); }       // замена reactive
</script>
<template><li v-for="(x, i) in list" :key="i" v-if="x.active">{{ x.name }}</li></template>
```

> [!question]- Ответ
> Потеря реактивности при деструктуризации и присваивании `list`, `v-if` вместе с `v-for`, ключ по индексу; исправление — `ref`/`toRefs`, `computed` для фильтрации, `key = x.id`.

## Как вести себя на live coding

1. Уточните требования (props, события, доступность, состояния).
2. Набросайте интерфейс компонента (props/emits/slots), затем реализацию.
3. Обработайте состояния: loading/empty/error.
4. Учитывайте доступность и очистку ресурсов.
5. Назовите, что бы добавили (тесты, оптимизация).

## Связанные темы

- [[N:3ea3310486798103be1ff9a1db673c18]]
- [[N:3ea331048679815f8ab2fd34e863ccd4]]
