---
type: topic
domain: frontend
stage: 5
section: "5.5"
order: 7
status: todo
level: middle
notion_id: 3ea33104867981858e18c06e049a568c
tags: [domain/frontend, stage/5, level/middle, topic/auth, topic/tokens, topic/storage, topic/security, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Хранение токенов и их обновление

↑ [[FE 5.5 Аутентификация и доступ — Keycloak, SSO, ACL|5.5 Аутентификация и доступ: Keycloak, SSO, ACL]] · ← [[FE 5.5.6 keycloak-js — интеграция во Vue|Предыдущая]] · → [[FE 5.5.8 ACL и RBAC на фронтенде|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> «Где хранить токен?» — вопрос с компромиссами XSS и CSRF.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Место | XSS | CSRF | Переживает перезагрузку | Комментарий |
|---|---|---|---|---|
| Память (переменная/Pinia без persist) | сложнее украсть постоянно, но скрипт в странице всё равно может вызвать API | нет | нет | лучший вариант для access; восстановление через refresh cookie |
| `localStorage` / `sessionStorage` | **токен читаем любым скриптом** | нет | да / вкладка | распространено, но рискованно при XSS |
| `HttpOnly` cookie | не читается JS | **уязвимость к CSRF** — нужны `SameSite`, CSRF-токены | да | предпочтительно для refresh и сессий |
| BFF (сервер хранит токены) | токенов в браузере нет | защита CSRF | да (cookie сессии) | наиболее безопасная схема для SPA |
| IndexedDB, Service Worker | как localStorage | — | да | не лучше |

Рекомендуемая схема:

1. **Access token** — в памяти.
2. **Refresh token** — `HttpOnly; Secure; SameSite` cookie (или полностью на BFF).
3. При загрузке страницы — silent refresh через cookie → access в память.
4. Ротация refresh-токена, отзыв при выходе.
5. Строгий CSP, экранирование, обновление зависимостей (снижают риск XSS).

Обновление в нескольких вкладках:

```ts
const lock = navigator.locks;                                   // Web Locks: одна вкладка обновляет, остальные ждут
export async function refreshOnce() { return lock.request("refresh", async () => { if (tokenValid()) return; await doRefresh(); channel.postMessage("refreshed"); }); }
```

Выход: очистка стора, кэша Vue Query, IndexedDB, отзыв токена, редирект на `logout` IdP; синхронизация выхода между вкладками (`storage`/`BroadcastChannel`).

Дополнительно: Content Security Policy, Subresource Integrity, Trusted Types, отсутствие токенов в URL/логах/аналитике.

## Нюансы и подводные камни

- «Токен в `localStorage`» удобен, но любая XSS-уязвимость = кража токена.
- `HttpOnly` cookie без CSRF-защиты открывает CSRF.
- Долгоживущие access-токены увеличивают ущерб.
- Токены попадают в отчёты об ошибках и логи — фильтруйте (Sentry `beforeSend`).
- Логаут только на клиенте не отзывает токен на сервере.

## Практика

1. Реализуйте access в памяти + refresh в cookie с silent refresh.
2. Добавьте синхронизацию выхода между вкладками.
3. Настройте фильтрацию токенов в Sentry.

## Вопросы с ответами

> [!question]- Где безопаснее хранить токен?
> Access — в памяти, refresh — в `HttpOnly` cookie или на сервере (BFF); `localStorage` уязвим при XSS.

> [!question]- Что делать при выходе?
> Отозвать токены на сервере, очистить состояние и кэши, завершить SSO-сессию.

## Связанные темы

- [[N:3ea3310486798174b39ee7d325d982cd]]
- [[N:3ea33104867981959103d2c15e81596d]]
