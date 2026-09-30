---
type: topic
domain: frontend
stage: 1
section: "1.1"
order: 3
status: todo
level: junior
notion_id: 3ea3310486798147bcb9d8a88f44b639
tags: [domain/frontend, stage/1, level/junior, topic/web, topic/storage, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Хранилища: Cookies, localStorage, sessionStorage, IndexedDB

↑ [[FE 1.1 Как работает веб и браузер|1.1 Как работает веб и браузер]] · ← [[FE 1.1.2 HTTP-HTTPS — методы, статусы, заголовки, HTTP-2 и HTTP-3|Предыдущая]] · → [[FE 1.1.4 CORS и Same-Origin Policy|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->


























> [!info] Зачем это на собесе
> Где хранить токены и данные: вопрос о безопасности и объёмах.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Хранилище | Объём | Время жизни | Уходит на сервер | Доступ из JS |
|---|---|---|---|---|
| Cookie | ~4 КБ | до `Expires`/`Max-Age`/сессия | да, с каждым запросом | да (кроме `HttpOnly`) |
| localStorage | ~5 МБ | пока не очистят | нет | да |
| sessionStorage | ~5 МБ | вкладка | нет | да |
| IndexedDB | сотни МБ и больше | постоянно | нет | да, асинхронно |
| Cache API / Service Worker | по квоте | постоянно | нет | да |

Cookie-флаги:

| Флаг | Смысл |
|---|---|
| `HttpOnly` | недоступна из JS (защита от кражи через XSS) |
| `Secure` | только HTTPS |
| `SameSite=Lax/Strict/None` | ограничение отправки при кросс-сайтовых запросах (защита от CSRF) |
| `Domain`, `Path` | область действия |

```js
localStorage.setItem("theme", "dark");
JSON.parse(localStorage.getItem("cart") ?? "[]");

const db = await new Promise((res, rej) => {
  const r = indexedDB.open("app", 1);
  r.onupgradeneeded = () => r.result.createObjectStore("orders", { keyPath: "id" });
  r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
});
```

Выбор: сессия и аутентификация — `HttpOnly` cookie; настройки UI — localStorage; крупные офлайн-данные — IndexedDB (через обёртки `idb`, Dexie).

## Нюансы и подводные камни

- `localStorage` синхронный (блокирует главный поток) и уязвим к XSS — не храните в нём токены доступа без осознанного решения.
- В режиме приватного просмотра возможны ограничения и исключения при записи: оборачивайте в `try/catch`.
- Хранилища привязаны к origin, `storage`-события позволяют синхронизировать вкладки.
- Cookie отправляются с каждым запросом: не храните большие данные.
- Пользователь и браузер могут очистить данные — не считайте их надёжной базой.

## Практика

1. Сохраните тему оформления в localStorage и синхронизируйте между вкладками через событие `storage`.
2. Настройте cookie с `HttpOnly; Secure; SameSite=Lax` на сервере.
3. Сохраните 10 000 записей в IndexedDB и выполните поиск по индексу.

## Вопросы с ответами

> [!question]- Где хранить токен?
> Предпочтительно в `HttpOnly` cookie; хранение в `localStorage` делает его доступным для XSS.

> [!question]- Чем localStorage отличается от sessionStorage?
> Первый живёт постоянно, второй — до закрытия вкладки.

> [!question]- Зачем SameSite?
> Ограничивает отправку cookie при кросс-сайтовых запросах, снижая риск CSRF.

## Связанные темы

- [[N:3ea331048679817ab843d2d18cee2479]]
- [[N:3ea33104867981018b3ad263fdb490a3]]
