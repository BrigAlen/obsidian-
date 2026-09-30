---
type: topic
domain: frontend
stage: 7
section: "7.2"
order: 7
status: todo
level: senior
notion_id: 3ea33104867981ea9adbd31e7ce94938
tags: [domain/frontend, stage/7, level/senior, topic/virtualization, topic/lists, topic/performance, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Виртуализация длинных списков

↑ [[FE 7.2 Рендеринг и производительность|7.2 Рендеринг и производительность]] · ← [[FE 7.2.6 Оптимизация изображений и шрифтов|Предыдущая]] · → [[FE 7.2.8 Мемоизация и лишние ре-рендеры|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Частая задача: таблица на десятки тысяч строк. Показывает понимание стоимости DOM.

## Проблема

10 000 строк = сотни тысяч DOM-узлов: долгий рендер, много памяти, тормозящий скролл.

## Идея

Рендерим только **видимое окно** плюс небольшой буфер (overscan). Контейнеру задаём общую высоту, элементы позиционируем `transform: translateY`.

```vue
<script setup lang="ts">
import { useVirtualizer } from '@tanstack/vue-virtual'

const parentRef = ref<HTMLElement | null>(null)
const rowVirtualizer = useVirtualizer({
  count: rows.length,
  getScrollElement: () => parentRef.value,
  estimateSize: () => 40,
  overscan: 8,
})
</script>

<template>
  <div ref="parentRef" style="height: 600px; overflow: auto">
    <div :style="{ height: rowVirtualizer.getTotalSize() + 'px', position: 'relative' }">
      <div v-for="v in rowVirtualizer.getVirtualItems()" :key="v.key"
           :style="{ position: 'absolute', top: 0, transform: `translateY(${v.start}px)`, height: v.size + 'px' }">
        {{ rows[v.index].name }}
      </div>
    </div>
  </div>
</template>
```

Готовые решения: `@tanstack/vue-virtual`, `vue-virtual-scroller`, `q-virtual-scroll` (Quasar), `QTable` с `virtual-scroll`.

## Нюансы

- переменная высота: измерение (`measureElement`) или оценка;
- поиск по странице (Ctrl+F) не найдёт нерендеренные строки;
- доступность: `aria-rowcount`, `aria-rowindex`;
- альтернатива — пагинация и бесконечная прокрутка; для данных — серверная фильтрация.

## Вопросы с ответами

> [!question]- Когда виртуализация не нужна?
> Когда строк немного (до пары сотен) или можно ограничить объём пагинацией. Виртуализация усложняет доступность, поиск и печать.

> [!question]- Как обрабатывать строки переменной высоты?
> Измерять реальные размеры после рендера и обновлять оценки, либо использовать динамический virtualizer.
