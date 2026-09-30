---
type: topic
domain: frontend
stage: 7
section: "7.3"
order: 1
status: todo
level: senior
notion_id: 3ea33104867981379929e473bebb9334
tags: [domain/frontend, stage/7, level/senior, topic/security, topic/xss, topic/vue, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# XSS и v-html

↑ [[FE 7.3 Безопасность фронтенда|7.3 Безопасность фронтенда]] · → [[FE 7.3.2 CSRF|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> XSS — главная фронтенд-уязвимость. Нужно различать виды, знать защиту во Vue и опасные места.

## Что это

Cross-Site Scripting: злоумышленник внедряет свой JS на страницу, и тот выполняется от имени сайта — с доступом к cookies, localStorage, DOM и запросам пользователя.

## Виды

| Вид | Откуда payload |
|---|---|
| **Stored** | сохранён на сервере (комментарий, профиль) |
| **Reflected** | из URL или формы, возвращается в ответе |
| **DOM-based** | клиентский код сам вставляет данные небезопасно (`innerHTML`, `location.hash`) |

## Защита во Vue

Интерполяция `{{ }}` и `:attr` **экранируются автоматически**. Опасны:

- `v-html` — вставляет сырой HTML;
- `innerHTML`, `insertAdjacentHTML`, `document.write`;
- динамические `href`/`src` со значением `javascript:...`;
- шаблоны, собираемые из пользовательских строк (`compile` на клиенте);
- `eval`, `new Function`, `setTimeout(string)`.

```vue
<!-- опасно, если html приходит от пользователя -->
<div v-html="comment.html" />

<!-- безопасно -->
<div>{{ comment.text }}</div>
```

## Санитизация

Если нужен HTML (редактор, markdown), очищаем **DOMPurify** с белым списком:

```ts
import DOMPurify from 'dompurify'
const clean = DOMPurify.sanitize(dirty, { ALLOWED_TAGS: ['b', 'i', 'a', 'ul', 'li', 'p'], ALLOWED_ATTR: ['href'] })
```

Санитизировать нужно там, где рендерим (и на сервере при сохранении как второй слой).

## Слои защиты

1. Экранирование по умолчанию, отказ от `v-html`.
2. Санитизация HTML (DOMPurify).
3. **CSP** — запрет inline-скриптов.
4. Cookie токена с `HttpOnly`.
5. Валидация URL: только `http(s):`.
6. Trusted Types (Chrome) для DOM-приёмников.

## Вопросы с ответами

> [!question]- Защищает ли Vue от XSS?
> В шаблонах экранирует данные, но `v-html`, `innerHTML` и `javascript:`-ссылки остаются на ответственности разработчика.

> [!question]- Как безопасно показать HTML от пользователя?
> Пропустить через DOMPurify с белым списком тегов и атрибутов, дополнительно ограничить CSP.
