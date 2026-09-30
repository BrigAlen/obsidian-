---
type: topic
domain: frontend
stage: 5
section: "5.2"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981ccbb11cc4932778fa7
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/pinia, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Pinia: state, getters, actions

↑ [[FE 5.2 Состояние — Pinia, SSOT, Vue Query|5.2 Состояние: Pinia, SSOT, Vue Query]] · ← [[FE 5.2.1 Зачем нужен state manager, локальное и глобальное состояние|Предыдущая]] · → [[FE 5.2.3 Pinia — Options и Setup stores|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Pinia — стандартный стор Vue 3. Спрашивают структуру и как работать с реактивностью.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
// stores/auth.ts
export const useAuthStore = defineStore("auth", {
  state: () => ({ user: null as User | null, token: "" as string, loading: false }),
  getters: {
    isAuthenticated: (s) => !!s.token,
    fullName(): string { return `${this.user?.first ?? ""} ${this.user?.last ?? ""}`.trim(); },
    hasRole: (s) => (role: string) => s.user?.roles.includes(role) ?? false,      // геттер-функция
  },
  actions: {
    async login(email: string, password: string) {
      this.loading = true;
      try { const r = await api.login(email, password); this.user = r.user; this.token = r.token; }
      finally { this.loading = false; }
    },
    logout() { this.$reset(); },
  },
});
```

```vue
<script setup>
const auth = useAuthStore();
const { user, isAuthenticated } = storeToRefs(auth);      // реактивная деструктуризация state/getters
const { login } = auth;                                    // actions деструктурируются напрямую
</script>
```

| Часть | Аналог | Правила |
|---|---|---|
| `state` | `data` | функция, возвращающая объект; типизируйте |
| `getters` | `computed` | кэшируются, могут использовать другие getters, принимать аргументы через возврат функции |
| `actions` | `methods` | синхронные и асинхронные, любая логика, доступ к `this` |

Особенности:

- Мутировать state можно напрямую (`store.count++`), через `$patch({...})` (пакетно) или в actions.
- `store.$reset()`, `$subscribe` (реакция на изменения), `$onAction` (перехват actions), `$state`.
- Сторы можно вызывать друг из друга (внутри actions).
- Отладка: Vue DevTools показывает состояние, историю изменений, time travel.
- Нет мутаций (в отличие от Vuex) и вложенных модулей — каждый стор независим.

## Нюансы и подводные камни

- Деструктуризация state без `storeToRefs` теряет реактивность.
- Использование стора вне компонента (например, в роутере) — только после `app.use(pinia)` или с передачей `pinia`.
- Getter с аргументом не кэшируется (возвращает функцию).
- Нельзя хранить в state несериализуемое (для SSR/devtools), исключение — осознанные.

## Практика

1. Создайте `auth`-стор с логином, выходом и геттерами ролей.
2. Используйте `$patch` и `$subscribe` для сохранения в `localStorage`.
3. Вызовите один стор из другого.

## Вопросы с ответами

> [!question]- Из чего состоит Pinia-стор?
> Из `state`, `getters` и `actions` (аналоги `data`, `computed`, `methods`).

> [!question]- Зачем `storeToRefs`?
> Чтобы деструктурировать state и getters, сохранив реактивность.

## Связанные темы

- [[N:3ea33104867981c4bc74e169ee2b8199]]
- [[N:3ea33104867981dc9c17f29411b85b4e]]
