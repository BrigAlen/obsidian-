---
type: topic
domain: frontend
stage: 7
section: "7.4"
order: 1
status: todo
level: senior
notion_id: 3ea33104867981a1abd0fa6ce0215ffb
tags: [domain/frontend, stage/7, level/senior, topic/browser-api, topic/observers, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# IntersectionObserver, ResizeObserver, MutationObserver

↑ [[FE 7.4 Browser API|7.4 Browser API]] · → [[FE 7.4.2 requestAnimationFrame и requestIdleCallback|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Три observer-а заменяют scroll-слушатели и опрос DOM. Спрашивают, когда какой применять.

## IntersectionObserver

Сообщает, когда элемент входит в область видимости (viewport или контейнер).

```ts
const io = new IntersectionObserver(
  entries => entries.forEach(e => {
    if (e.isIntersecting) { loadImage(e.target as HTMLImageElement); io.unobserve(e.target) }
  }),
  { root: null, rootMargin: '200px', threshold: 0.1 },
)
io.observe(el)
```

Применение: lazy loading, бесконечная прокрутка (sentinel-элемент), аналитика видимости, подсветка пункта меню, ленивая гидрация.

## ResizeObserver

Реагирует на изменение размера **элемента** (а не окна).

```ts
const ro = new ResizeObserver(([entry]) => {
  const { width } = entry.contentRect
  compact.value = width < 480
})
ro.observe(container)
```

Применение: адаптивные компоненты (container-based), графики, виртуальные списки, авторазмер textarea.

Нюанс: изменение размера внутри колбэка может вызвать цикл (`ResizeObserver loop`), используйте `requestAnimationFrame`.

## MutationObserver

Следит за изменениями DOM (дети, атрибуты, текст).

```ts
const mo = new MutationObserver(list => list.forEach(m => console.log(m.type)))
mo.observe(el, { childList: true, attributes: true, subtree: true })
```

Применение: интеграция со сторонним кодом, расширения, определение появления элемента. Во Vue редко нужен: реактивность заменяет.

## Composable

```ts
export function useElementSize(el: Ref<HTMLElement | null>) {
  const size = reactive({ width: 0, height: 0 })
  let ro: ResizeObserver
  onMounted(() => {
    ro = new ResizeObserver(([e]) => { size.width = e.contentRect.width; size.height = e.contentRect.height })
    if (el.value) ro.observe(el.value)
  })
  onBeforeUnmount(() => ro?.disconnect())
  return size
}
```

Готовые: VueUse (`useIntersectionObserver`, `useElementSize`, `useMutationObserver`).

## Всегда отключайте

`disconnect()` или `unobserve()` при размонтировании, иначе утечка.

## Вопросы с ответами

> [!question]- Почему IntersectionObserver лучше scroll-события?
> Работает асинхронно вне основного потока обработки прокрутки, не вызывает layout при каждом событии, браузер оптимизирует проверки.

> [!question]- Чем ResizeObserver лучше window.resize?
> Следит за размером конкретного элемента, а не окна: подходит для компонентов, которые меняют размер от макета.
