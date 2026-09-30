---
type: topic
domain: frontend
stage: 8
section: "8.1"
order: 5
status: todo
level: senior
notion_id: 3ea33104867981108787cd7978d897f3
tags: [domain/frontend, stage/8, level/senior, topic/declarative, topic/imperative, topic/vue, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Декларативный и императивный подход

↑ [[FE 8.1 Парадигмы — ООП, ФП, SOLID|8.1 Парадигмы: ООП, ФП, SOLID]] · ← [[FE 8.1.4 ФП — функции высшего порядка, compose и pipe|Предыдущая]] · → [[FE 8.1.6 Реактивное программирование и RxJS (обзорно)|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Объясняет, почему Vue и React «проще» jQuery, и когда императивный код неизбежен.

## Различие

- **Императивный**: описываем *как* сделать по шагам (управляем состоянием и DOM).
- **Декларативный**: описываем *что* хотим получить, а исполнение делегируем платформе или фреймворку.

```ts
// императивно (jQuery-подход)
const list = document.getElementById('list')!
list.innerHTML = ''
for (const u of users) {
  if (!u.active) continue
  const li = document.createElement('li')
  li.textContent = u.name
  list.appendChild(li)
}
```

```vue
<!-- декларативно -->
<ul>
  <li v-for="u in users.filter(u => u.active)" :key="u.id">{{ u.name }}</li>
</ul>
```

```ts
// данные: императивно и декларативно
let total = 0
for (const o of orders) if (o.paid) total += o.sum

const total2 = orders.filter(o => o.paid).reduce((s, o) => s + o.sum, 0)
```

## Что даёт декларативность

- меньше ручного управления состоянием DOM;
- UI = функция(состояние);
- проще читать, тестировать, оптимизировать фреймворком;
- меньше багов рассинхронизации.

## Примеры в стеке

CSS, HTML, SQL, шаблоны Vue, Router-конфиг, XState-машины, Terraform/Kubernetes — декларативные описания.

## Где нужен императивный код

- работа с Canvas и WebGL;
- фокус, скролл, измерение DOM (через `ref` и хуки);
- интеграция сторонних библиотек (карты, графики);
- критичные по производительности участки.

Хорошая практика: императивный код прячем за декларативным интерфейсом (компонент-обёртка, директива, composable).

## Вопросы с ответами

> [!question]- Чем декларативный подход лучше?
> Описываем желаемый результат, а не шаги: меньше ошибок синхронизации состояния, лучше читаемость, фреймворк оптимизирует обновления.

> [!question]- Как сочетать с императивным API сторонней библиотеки?
> Обернуть в компонент или composable: снаружи props и события, внутри `onMounted`/`onBeforeUnmount` и watch для синхронизации.
