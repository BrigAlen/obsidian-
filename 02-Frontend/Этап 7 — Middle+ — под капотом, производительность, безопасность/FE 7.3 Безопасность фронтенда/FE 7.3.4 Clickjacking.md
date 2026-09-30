---
type: topic
domain: frontend
stage: 7
section: "7.3"
order: 4
status: todo
level: senior
notion_id: 3ea331048679817c97aee4d6b2f9c8c3
tags: [domain/frontend, stage/7, level/senior, topic/security, topic/clickjacking, topic/headers, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Clickjacking

↑ [[FE 7.3 Безопасность фронтенда|7.3 Безопасность фронтенда]] · ← [[FE 7.3.3 CSP|Предыдущая]] · → [[FE 7.3.5 Безопасное хранение токенов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Небольшая, но частая тема: проверяют, знаете ли вы заголовки против встраивания.

## Суть

Злоумышленник встраивает ваш сайт в невидимый `iframe` на своей странице и заманивает пользователя кликнуть, «нажимая» на скрытую кнопку (подтвердить перевод, удалить аккаунт).

## Защита

| Способ | Пример |
|---|---|
| Заголовок `X-Frame-Options` | `DENY` или `SAMEORIGIN` (устаревающий) |
| CSP `frame-ancestors` | `frame-ancestors 'none'` или `'self'` |
| SameSite cookie | в iframe чужого сайта cookie не отправятся |
| Подтверждение опасных действий | пароль, 2FA, повторный ввод |

Frame busting через JS (`if (top !== self)`) — ненадёжно, не полагайтесь.

```nginx
add_header X-Frame-Options "DENY" always;
add_header Content-Security-Policy "frame-ancestors 'none'" always;
```

## Нюансы

- если нужно легитимное встраивание (виджеты), укажите точные домены в `frame-ancestors`;
- для своих iframe используйте `sandbox` и минимальные разрешения;
- похожие атаки: UI redressing, cursorjacking.

## Вопросы с ответами

> [!question]- Как запретить встраивание сайта в iframe?
> `Content-Security-Policy: frame-ancestors 'none'` (или `'self'`), для старых браузеров ещё `X-Frame-Options`.
