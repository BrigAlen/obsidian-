---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 22
status: todo
level: middle
notion_id: 3ea33104867981b2a2b2e2ba946e571c
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/vueuse, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# VueUse

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.21 Composables|Предыдущая]] · → [[FE 4.1.23 Плагины Vue|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Знание готовых composables экономит время: `useStorage`, `useDebounceFn`, `useEventListener`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**VueUse** — коллекция сотен composables на Composition API (`@vueuse/core`, `@vueuse/integrations`, `@vueuse/router` и др.).

| Категория | Примеры |
|---|---|
| Состояние | `useStorage`, `useLocalStorage`, `useToggle`, `useCounter`, `useRefHistory` |
| Элементы | `useElementSize`, `useIntersectionObserver`, `useResizeObserver`, `onClickOutside`, `useFocus` |
| Браузер | `useTitle`, `useClipboard`, `useDark`, `usePreferredDark`, `useMediaQuery`, `useBreakpoints`, `useFullscreen`, `useShare` |
| Сенсоры и события | `useEventListener`, `useMouse`, `useKeyModifier`, `onKeyStroke`, `useSwipe` |
| Сеть | `useFetch`, `useWebSocket`, `useOnline`, `useEventSource` |
| Утилиты | `useDebounceFn`, `useThrottleFn`, `useTimeout`, `useInterval`, `useNow`, `useTimeAgo`, `refDebounced`, `watchDebounced`, `useVModel` |
| Анимация | `useTransition`, `useRafFn` |
| Интеграции | `useAxios`, `useQRCode`, `useSortable`, `useFuse` |

```ts
import { useLocalStorage, useDebounceFn, useEventListener, onClickOutside, useDark, useIntersectionObserver } from "@vueuse/core";

const prefs = useLocalStorage("prefs", { theme: "light", perPage: 20 });       // реактивно и синхронно с хранилищем
const search = useDebounceFn((q: string) => load(q), 300);
const dark = useDark();
const target = ref<HTMLElement | null>(null);
onClickOutside(target, () => (open.value = false));
useEventListener(window, "resize", onResize);                                  // автоматическая очистка
const { stop } = useIntersectionObserver(sentinel, ([{ isIntersecting }]) => isIntersecting && loadMore());
```

Преимущества: очистка ресурсов автоматически (привязка к области), SSR-безопасность, tree-shaking, типы.

Когда не подходит: если нужен один маленький хелпер — проще написать самому; следите за размером зависимостей.

## Нюансы и подводные камни

- Не зависите слепо от сложных composables (например, `useFetch`) — для API лучше TanStack Query.
- Проверяйте поддержку API в целевых браузерах.
- Версии `@vueuse/*` пакетов должны совпадать.
- Прежде чем писать свой composable, посмотрите VueUse.

## Практика

1. Замените ручные слушатели событий и таймеры на VueUse.
2. Реализуйте тёмную тему через `useDark`.
3. Сделайте бесконечную прокрутку через `useIntersectionObserver`.

## Вопросы с ответами

> [!question]- Что такое VueUse?
> Набор готовых composables для браузерных API, состояния и утилит.

> [!question]- Чем полезна привязка к области видимости?
> Слушатели и таймеры очищаются автоматически при уничтожении компонента.

## Связанные темы

- [[N:3ea33104867981c78367f30abc89391d]]
- [[N:3ea33104867981c1ae13c70ac05504c1]]
