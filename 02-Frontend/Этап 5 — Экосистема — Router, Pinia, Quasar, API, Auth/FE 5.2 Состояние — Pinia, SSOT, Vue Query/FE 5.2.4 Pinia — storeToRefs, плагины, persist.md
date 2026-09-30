---
type: topic
domain: frontend
stage: 5
section: "5.2"
order: 4
status: todo
level: middle
notion_id: 3ea331048679816d9550cadc1c99705d
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/pinia, topic/plugins, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Pinia: storeToRefs, плагины, persist

↑ [[FE 5.2 Состояние — Pinia, SSOT, Vue Query|5.2 Состояние: Pinia, SSOT, Vue Query]] · ← [[FE 5.2.3 Pinia — Options и Setup stores|Предыдущая]] · → [[FE 5.2.5 Pinia и Vuex — различия|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Расширение Pinia: сохранение состояния, плагины, безопасность данных.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**`storeToRefs(store)`** возвращает refs для state и getters (actions берутся напрямую).

```ts
const store = useUiStore();
const { theme, sidebarOpen } = storeToRefs(store);
const { toggleSidebar } = store;
```

**Плагин Pinia** — функция, получающая контекст (`store`, `app`, `pinia`, `options`).

```ts
const logger: PiniaPlugin = ({ store }) => {
  store.$onAction(({ name, args, after, onError }) => {
    const t = performance.now();
    after(() => console.debug(`${store.$id}.${name}`, args, `${performance.now() - t} мс`));
    onError((e) => report(e));
  });
  store.$subscribe((mutation, state) => localStorage.setItem(`pinia:${store.$id}`, JSON.stringify(state)));
};
const pinia = createPinia().use(logger);

declare module "pinia" { export interface PiniaCustomProperties { $api: ApiClient } }   // типизация добавленных свойств
```

**Persist** (`pinia-plugin-persistedstate`):

```ts
pinia.use(piniaPluginPersistedstate);
export const useSettings = defineStore("settings", () => { /* ... */ }, {
  persist: { key: "settings", storage: localStorage, pick: ["theme", "locale"] },   // только нужные поля
});
```

Что сохранять: тему, язык, черновики, выбранные фильтры. **Чего не сохранять:** токены доступа в `localStorage` без осознанного решения (XSS), персональные данные, кэш сервера.

Другие возможности: `$state` (замена состояния), `pinia.state.value` (SSR-гидратация), `defineStore` с `hydrate`, **HMR** (`acceptHMRUpdate`), тестирование (`createTestingPinia`), `setActivePinia` вне компонентов.

## Нюансы и подводные камни

- Не забывайте, что при SSR состояние сериализуется: только JSON-совместимое.
- Persist при изменении структуры стора ломает старые сохранённые данные: версионируйте ключи, миграции.
- Плагины выполняются для каждого стора — используйте фильтр по `store.$id`.
- Токены лучше хранить в `HttpOnly` cookie.

## Практика

1. Настройте `persist` для темы и языка, исключив чувствительное.
2. Напишите плагин логирования actions.
3. Реализуйте версионирование сохранённого состояния.

## Вопросы с ответами

> [!question]- Что делает `storeToRefs`?
> Превращает state и getters стора в `ref`, чтобы деструктурировать без потери реактивности.

> [!question]- Что нельзя хранить в persist?
> Секреты и чувствительные данные (токены, персональные данные) без защиты; кэш серверных данных.

## Связанные темы

- [[N:3ea33104867981dc9c17f29411b85b4e]]
- [[N:3ea33104867981f9ba40db4b92a30f89]]
