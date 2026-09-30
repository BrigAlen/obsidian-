---
type: topic
domain: frontend
stage: 7
section: "7.3"
order: 2
status: todo
level: senior
notion_id: 3ea33104867981d8ba19c2089038954c
tags: [domain/frontend, stage/7, level/senior, topic/security, topic/csrf, topic/cookies, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# CSRF

↑ [[FE 7.3 Безопасность фронтенда|7.3 Безопасность фронтенда]] · ← [[FE 7.3.1 XSS и v-html|Предыдущая]] · → [[FE 7.3.3 CSP|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Атака на cookie-аутентификацию; проверяют, понимаете ли вы SameSite и токены.

## Суть

Cross-Site Request Forgery: чужой сайт заставляет браузер пользователя отправить запрос на ваш сайт. Браузер **сам прикладывает cookie**, и действие выполняется от имени жертвы.

```html
<!-- на evil.com -->
<form action="https://bank.com/transfer" method="POST">
  <input name="to" value="attacker"><input name="sum" value="1000">
</form>
<script>document.forms[0].submit()</script>
```

## Защита

| Механизм | Описание |
|---|---|
| **SameSite** cookie | `Lax` (по умолчанию в браузерах) и `Strict` не отправляют cookie при кросс-сайтовых запросах |
| **CSRF-токен** | случайное значение в форме или заголовке, проверяется сервером |
| **Double-submit cookie** | токен в cookie и в заголовке должны совпасть |
| **Проверка Origin/Referer** | сервер отвергает чужие источники |
| **Кастомный заголовок** | простые формы не могут его поставить без CORS-preflight |
| **Bearer-токен в заголовке** | браузер сам не подставляет, CSRF неактуален (но есть XSS-риск) |

```ts
axios.defaults.xsrfCookieName = 'XSRF-TOKEN'
axios.defaults.xsrfHeaderName = 'X-XSRF-TOKEN'
axios.defaults.withCredentials = true
```

## Нюансы

- GET-запросы не должны менять состояние;
- `SameSite=None` требует `Secure`, а значит нужны токены;
- CORS сам по себе от CSRF не защищает (запрос всё равно уходит);
- поддомены считаются одним «сайтом» (site) для SameSite.

## Вопросы с ответами

> [!question]- Чем CSRF отличается от XSS?
> XSS исполняет чужой код в вашем сайте, CSRF использует доверие сайта к браузеру пользователя, отправляя запросы с чужой страницы. XSS обходит любую CSRF-защиту.

> [!question]- Спасёт ли SameSite=Lax?
> Защитит от большинства кросс-сайтовых POST. Но для чувствительных операций всё равно нужны токены, а GET-запросы не должны менять данные.
