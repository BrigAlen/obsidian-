---
type: topic
domain: frontend
stage: 7
section: "7.4"
order: 9
status: todo
level: senior
notion_id: 3ea33104867981a2af8bc91606799ac8
tags: [domain/frontend, stage/7, level/senior, topic/browser-api, topic/web-components, topic/shadow-dom, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Web Components и Shadow DOM

↑ [[FE 7.4 Browser API|7.4 Browser API]] · ← [[FE 7.4.8 Canvas и SVG|Предыдущая]] · → [[FE 7.4.10 PWA и Service Workers|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Нативные компоненты: для микрофронтендов и библиотек без привязки к фреймворку.

## Три технологии

1. **Custom Elements** — свои теги с жизненным циклом.
2. **Shadow DOM** — изолированное поддерево: стили не «протекают» ни внутрь, ни наружу.
3. **HTML templates и slots** — шаблоны и проекция контента.

```ts
class UserBadge extends HTMLElement {
  static observedAttributes = ['name']
  #root = this.attachShadow({ mode: 'open' })
  connectedCallback() { this.render() }
  attributeChangedCallback() { this.render() }
  render() {
    this.#root.innerHTML = `
      <style>:host { display: inline-block } .b { padding: 2px 8px; border-radius: 8px }</style>
      <span class="b"><slot></slot> ${this.getAttribute('name') ?? ''}</span>`
  }
}
customElements.define('user-badge', UserBadge)
```

Жизненный цикл: `connectedCallback`, `disconnectedCallback`, `attributeChangedCallback`, `adoptedCallback`.

## Стили и Shadow DOM

- внутри shadow-root — свои стили, глобальные не действуют;
- наружу открываем настройку через **CSS custom properties** (`--badge-color`) и `::part(name)`;
- `:host`, `:host-context`, `::slotted()`.

## Vue и Web Components

```ts
import { defineCustomElement } from 'vue'
const MyElement = defineCustomElement(MyComponent)
customElements.define('my-element', MyElement)
```

Использование Web Components в Vue: `compilerOptions.isCustomElement: tag => tag.startsWith('my-')`.

## Когда использовать

Дизайн-система для нескольких фреймворков, виджеты для встраивания на чужие сайты, микрофронтенды с изоляцией. Минусы: SSR, формы (ElementInternals), доступность и теневые границы требуют внимания.

## Вопросы с ответами

> [!question]- Зачем Shadow DOM?
> Инкапсуляция стилей и разметки: внешние стили не ломают компонент, стили компонента не влияют на страницу.

> [!question]- Как стилизовать Web Component снаружи?
> Через CSS-переменные (наследуются в shadow) и `::part()`, если автор компонента открыл части.
