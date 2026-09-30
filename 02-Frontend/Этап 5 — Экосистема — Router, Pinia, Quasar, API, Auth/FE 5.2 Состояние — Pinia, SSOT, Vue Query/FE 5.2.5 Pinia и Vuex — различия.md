---
type: topic
domain: frontend
stage: 5
section: "5.2"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981f9ba40db4b92a30f89
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/pinia, topic/vuex, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Pinia и Vuex: различия

↑ [[FE 5.2 Состояние — Pinia, SSOT, Vue Query|5.2 Состояние: Pinia, SSOT, Vue Query]] · ← [[FE 5.2.4 Pinia — storeToRefs, плагины, persist|Предыдущая]] · → [[FE 5.2.6 Паттерн SSOT (Single Source of Truth)|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Легаси на Vuex ещё встречается; ждут перечня отличий и понимания миграции.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Аспект | Vuex | Pinia |
|---|---|---|
| Статус | режим поддержки | официальный стор Vue |
| Мутации | обязательны (`mutations` синхронные + `actions`) | нет: state меняют напрямую или в actions |
| Модули | вложенные `modules`, пространства имён | независимые сторы, композиция через импорт |
| TypeScript | сложная типизация | естественная, вывод типов |
| API | Options; `mapState/mapGetters/mapActions` | Options и Setup, `storeToRefs` |
| Composition API | обходные пути | нативно |
| DevTools | да | да, time travel, история |
| SSR/HMR | да | да, проще |
| Размер | больше | ~1 КБ |
| Плагины | есть | есть, типизированные |

```js
// Vuex
mutations: { SET_USER(state, u) { state.user = u; } },
actions: { async login({ commit }, creds) { commit("SET_USER", await api.login(creds)); } },

// Pinia
actions: { async login(creds) { this.user = await api.login(creds); } }
```

Миграция: переносить модуль за модулем; `Vuex` и `Pinia` могут сосуществовать; заменять `mapState` на `storeToRefs`, мутации — на прямые изменения/actions, `namespaced` модули — на отдельные сторы (`useXxxStore`), `rootState` — на импорт другого стора.

Причины ухода от Vuex: многословность (мутации), слабая типизация, вложенные модули, сложность масштабирования.

## Нюансы и подводные камни

- Мутации давали трассировку изменений — в Pinia её обеспечивает DevTools и `$onAction`/`$subscribe`.
- Прямое изменение state из компонентов поощряет разбросанные мутации: договоритесь о правилах (изменения через actions).
- В Vuex-проекте с большим числом модулей миграцию планируйте по частям.
- Плагины Vuex не совместимы с Pinia.

## Практика

1. Перенесите один Vuex-модуль в Pinia-стор.
2. Замените `mapState/mapActions` в компонентах.
3. Оцените объём кода до и после.

## Вопросы с ответами

> [!question]- Основные отличия Pinia от Vuex?
> Нет мутаций и вложенных модулей, лучшая типизация, нативная поддержка Composition API, независимые сторы.

> [!question]- Куда исчезли мутации?
> Состояние изменяется напрямую или в actions; отслеживание обеспечивают DevTools и подписки.

## Связанные темы

- [[N:3ea331048679816d9550cadc1c99705d]]
- [[N:3ea33104867981a29097d09f135f1a79]]
