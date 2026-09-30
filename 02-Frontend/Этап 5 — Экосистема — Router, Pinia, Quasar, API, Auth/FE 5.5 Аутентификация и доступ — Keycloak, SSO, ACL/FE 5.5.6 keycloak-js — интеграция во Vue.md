---
type: topic
domain: frontend
stage: 5
section: "5.5"
order: 6
status: todo
level: middle
notion_id: 3ea3310486798174b39ee7d325d982cd
tags: [domain/frontend, stage/5, level/middle, topic/auth, topic/keycloak, topic/vue, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# keycloak-js: интеграция во Vue

↑ [[FE 5.5 Аутентификация и доступ — Keycloak, SSO, ACL|5.5 Аутентификация и доступ: Keycloak, SSO, ACL]] · ← [[FE 5.5.5 SSO и Keycloak — realm, client, roles|Предыдущая]] · → [[FE 5.5.7 Хранение токенов и их обновление|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Практика: инициализация Keycloak до старта приложения, обновление токена и выход.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
// auth/keycloak.ts
import Keycloak from "keycloak-js";
export const keycloak = new Keycloak({ url: import.meta.env.VITE_KC_URL, realm: import.meta.env.VITE_KC_REALM, clientId: import.meta.env.VITE_KC_CLIENT });

export async function initAuth(): Promise<boolean> {
  const authenticated = await keycloak.init({
    onLoad: "check-sso",                              // не форсировать логин; "login-required" — принудительно
    pkceMethod: "S256",
    silentCheckSsoRedirectUri: `${location.origin}/silent-check-sso.html`,
    checkLoginIframe: false,                          // iframe-проверка ломается без сторонних cookie
  });
  keycloak.onTokenExpired = () => keycloak.updateToken(30).catch(() => keycloak.login());
  keycloak.onAuthLogout = () => useAuthStore().clear();
  return authenticated;
}
```

```ts
// main.ts: перед монтированием приложения
await initAuth();
createApp(App).use(pinia).use(router).mount("#app");

// stores/auth.ts
export const useAuthStore = defineStore("auth", () => {
  const user = computed(() => keycloak.tokenParsed && { id: keycloak.tokenParsed.sub, name: keycloak.tokenParsed.preferred_username });
  const roles = computed<string[]>(() => keycloak.tokenParsed?.realm_access?.roles ?? []);
  const hasRole = (r: string) => roles.value.includes(r);
  const login = () => keycloak.login({ redirectUri: location.href });
  const logout = () => keycloak.logout({ redirectUri: location.origin });
  async function getToken() { await keycloak.updateToken(30); return keycloak.token!; }    // актуальный токен для запросов
  return { user, roles, hasRole, login, logout, getToken, isAuthenticated: computed(() => !!keycloak.authenticated) };
});
```

```ts
// Интерсептор Axios: токен в каждом запросе
api.interceptors.request.use(async (cfg) => { const t = await useAuthStore().getToken(); cfg.headers.Authorization = `Bearer ${t}`; return cfg; });

// Guard роутера
router.beforeEach((to) => { if (to.meta.requiresAuth && !keycloak.authenticated) return keycloak.login({ redirectUri: location.origin + to.fullPath }) as never; });
```

Реактивность: `keycloak` сам по себе не реактивен — оборачивайте в стор и обновляйте `ref` в колбэках (`onAuthSuccess`, `onTokenExpired`).

Альтернативы: `oidc-client-ts` (универсальнее, не привязан к Keycloak), `vue-keycloak-js`, `@dsb-norge/vue-keycloak-js`.

Тестирование: мок `keycloak` (`vi.mock("@/auth/keycloak")`), подстановка стора (`createTestingPinia`).

## Нюансы и подводные камни

- Инициализация должна завершиться до первого рендера и guard-ов.
- `updateToken(minValidity)` обновляет только при близком истечении — вызывайте перед каждым запросом.
- Ошибка обновления (истёк refresh) → повторный вход.
- Бесконечные редиректы при неверных URL/redirect.
- Токены не хранятся в Pinia persist.

## Практика

1. Подключите Keycloak к Vue-приложению с `check-sso` и guard-ами.
2. Добавьте токен в запросы и обработайте истечение refresh.
3. Замокайте Keycloak в тестах.

## Вопросы с ответами

> [!question]- `check-sso` или `login-required`?
> `check-sso` проверяет существующую сессию без принудительного логина (публичные страницы возможны), `login-required` перенаправляет неавторизованных на вход.

> [!question]- Как обновлять токен?
> `keycloak.updateToken(minValidity)` перед запросами и по событию `onTokenExpired`.

## Связанные темы

- [[N:3ea33104867981ab949ccb7b17f78719]]
- [[N:3ea33104867981858e18c06e049a568c]]
