---
type: topic
domain: frontend
stage: 7
section: "7.1"
order: 4
status: todo
level: senior
notion_id: 3ea3310486798188b17cdd9108d27d74
tags: [domain/frontend, stage/7, level/senior, topic/vue, topic/vdom, topic/compiler, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Virtual DOM, рендер-функции, компилятор

↑ [[FE 7.1 Vue под капотом|7.1 Vue под капотом]] · ← [[FE 7.1.3 effectScope, markRaw, readonly, customRef|Предыдущая]] · → [[FE 7.1.5 Алгоритм diff и роль key|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Вопрос «как Vue быстрее чистого virtual DOM»: компилятор оптимизирует шаблон на этапе сборки.

## Virtual DOM

Это дерево JS-объектов (vnode), описывающих DOM. При обновлении Vue строит новое дерево, сравнивает со старым и применяет **минимальные изменения** к настоящему DOM.

## Рендер-функции

```ts
import { h } from 'vue'
export default {
  props: ['level'],
  setup(props, { slots }) {
    return () => h(`h${props.level}`, { class: 'title' }, slots.default?.())
  },
}
```

Шаблоны компилируются в такие функции. Рендер-функции (и JSX) удобны для динамических компонентов и библиотек.

## Компилятор: оптимизации

| Приём | Смысл |
|---|---|
| **Static hoisting** | статические узлы создаются один раз вне render |
| **Patch flags** | у динамических узлов помечено, что менять (`TEXT`, `CLASS`, `PROPS`) |
| **Block tree** | обход только динамических узлов блока, а не всего дерева |
| **Cache handlers** | обработчики событий кэшируются |
| **Inline text** | склейка соседних статических строк |

Пример: в `<div><p>static</p><span>{{ msg }}</span></div>` при обновлении проверяется только `span`, причём только текст.

## Нюансы

- оптимизации работают только для шаблонов, в ручных рендер-функциях их нет;
- `v-once` и `v-memo` дополнительно отключают или ограничивают патчинг;
- в Vue 3.6 Vapor Mode может вовсе отказаться от virtual DOM (см. тему про новое).

## Вопросы с ответами

> [!question]- Что оптимизирует компилятор Vue?
> Поднимает статические узлы, ставит patch flags, строит block tree для обхода только динамических частей, кэширует обработчики.

> [!question]- Когда писать рендер-функцию вместо шаблона?
> Для сильно динамической структуры (обёртки, таблицы, генерация заголовков уровня n). В остальных случаях шаблон эффективнее.
