---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 19
status: todo
level: middle
notion_id: 3ea33104867981d5912bd2c38599765c
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/built-in-components, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Встроенные компоненты: Transition, KeepAlive, Teleport, Suspense

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.18 Динамические компоненты — component —is|Предыдущая]] · → [[FE 4.1.20 Асинхронные компоненты и lazy loading|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Встроенные компоненты решают типовые UI-задачи: анимации, кэш, порталы, асинхронные зависимости.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Компонент | Задача |
|---|---|
| `<Transition>` | анимация появления/исчезновения одного элемента (CSS-классы `v-enter-active` и др., JS-хуки) |
| `<TransitionGroup>` | анимация списков (перемещение, добавление, удаление); требует `key` |
| `<KeepAlive>` | кэширует экземпляры компонентов при переключении (`include/exclude/max`) |
| `<Teleport to="body">` | рендер части шаблона в другом месте DOM (модальные окна, тултипы) |
| `<Suspense>` | ожидание асинхронных зависимостей (async setup, async components), `fallback` |

```vue
<Transition name="fade" mode="out-in">
  <p v-if="show" key="a">Текст</p>
</Transition>
<style>
.fade-enter-active, .fade-leave-active { transition: opacity .2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

<TransitionGroup name="list" tag="ul"><li v-for="i in items" :key="i.id">{{ i.t }}</li></TransitionGroup>

<KeepAlive :max="10"><component :is="view" /></KeepAlive>       <!-- onActivated/onDeactivated -->

<Teleport to="body"><div v-if="open" class="modal">...</div></Teleport>     <!-- избавляет от проблем z-index/overflow -->

<Suspense>
  <template #default><AsyncWidget /></template>
  <template #fallback><Spinner /></template>
</Suspense>
```

Особенности:

- **Transition**: работает с `v-if`, `v-show`, динамическими компонентами; режимы `in-out`/`out-in`; учитывайте `prefers-reduced-motion`.
- **KeepAlive**: хуки `activated/deactivated`, ограничение `max` (LRU), исключения по имени.
- **Teleport**: логика и события остаются в исходном компоненте; доступность — фокус-ловушка, `aria-modal`.
- **Suspense** — экспериментальный API (стабилен в использовании, но с ограничениями); `@resolve`, `@pending`, `@fallback`; вложенные Suspense.

Альтернатива Suspense в реальных приложениях: явные состояния загрузки (Vue Query) и скелетоны.

## Нюансы и подводные камни

- `Transition` требует единственный корневой элемент.
- Неверный `key` не запускает переход.
- `KeepAlive` увеличивает потребление памяти и может показывать устаревшие данные — обновляйте в `onActivated`.
- Teleport на несуществующий контейнер — ошибка/предупреждение.
- Suspense не ловит ошибки: нужен `onErrorCaptured`.

## Практика

1. Сделайте модальное окно на `Teleport` + `Transition`.
2. Кэшируйте вкладки через `KeepAlive` и обновляйте данные в `onActivated`.
3. Анимируйте добавление/удаление элементов через `TransitionGroup`.

## Вопросы с ответами

> [!question]- Для чего `Teleport`?
> Рендерит содержимое в другое место DOM (например, в `body`), сохраняя логику компонента и избегая проблем с `overflow`/`z-index`.

> [!question]- Что делает `KeepAlive`?
> Сохраняет экземпляры компонентов при переключении, не уничтожая состояние.

## Связанные темы

- [[N:3ea33104867981b38c0bfd41456db1be]]
- [[N:3ea33104867981fcb497fa1eaf2daa2e]]
