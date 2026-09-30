---
type: topic
domain: frontend
stage: 7
section: "7.3"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981b688cdc98186669b0f
tags: [domain/frontend, stage/7, level/senior, topic/security, topic/csp, topic/headers, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# CSP

↑ [[FE 7.3 Безопасность фронтенда|7.3 Безопасность фронтенда]] · ← [[FE 7.3.2 CSRF|Предыдущая]] · → [[FE 7.3.4 Clickjacking|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> CSP — второй эшелон защиты от XSS; вопросы: как настроить и как жить с inline-скриптами.

## Что это

Content-Security-Policy — заголовок, в котором сервер перечисляет, откуда разрешено грузить скрипты, стили, картинки, фреймы. Браузер блокирует остальное.

```text
Content-Security-Policy:
  default-src 'self';
  script-src 'self' 'nonce-r4nd0m';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https://cdn.example.com;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  base-uri 'self';
  object-src 'none'
```

## Директивы

| Директива | Что регулирует |
|---|---|
| `script-src` | источники JS |
| `style-src` | стили |
| `connect-src` | fetch, XHR, WebSocket |
| `img-src`, `font-src`, `media-src` | ресурсы |
| `frame-ancestors` | кто может встраивать страницу |
| `form-action` | куда отправляют формы |
| `upgrade-insecure-requests` | http → https |

## Как избавиться от unsafe-inline

- **nonce**: сервер генерирует случайное значение на каждый ответ, `<script nonce="...">`;
- **hash**: SHA-256 содержимого inline-скрипта;
- `strict-dynamic` — доверие к скриптам, загруженным доверенными скриптами.

## Внедрение

1. `Content-Security-Policy-Report-Only` + `report-to` — собрать нарушения без блокировок.
2. Разобрать источники, убрать лишнее.
3. Включить в блокирующем режиме.

## Нюансы

- `unsafe-eval` нужен некоторым рантаймам шаблонов (полный билд Vue с компилятором); используйте предкомпилированный билд;
- сторонние виджеты (аналитика, чат) усложняют политику;
- в SPA заголовок ставит nginx или CDN, `<meta http-equiv>` умеет не всё (нет `frame-ancestors`).

## Вопросы с ответами

> [!question]- Зачем CSP, если экранирование уже есть?
> Это защита в глубину: даже при найденной XSS браузер не выполнит inline-скрипт или не отправит данные на чужой домен.

> [!question]- Как безопасно внедрить CSP на существующем сайте?
> Начать с Report-Only, собрать отчёты, поправить источники, затем включить блокировку.
