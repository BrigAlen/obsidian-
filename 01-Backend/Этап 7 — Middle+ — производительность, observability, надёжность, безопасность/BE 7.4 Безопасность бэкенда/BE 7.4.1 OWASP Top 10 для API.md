---
type: topic
domain: backend
stage: 7
section: "7.4"
order: 1
status: todo
level: senior
notion_id: 3ea331048679819fb453ede68cd221d1
tags: [domain/backend, stage/7, level/senior, topic/security, topic/owasp, topic/api, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# OWASP Top 10 для API

↑ [[BE 7.4 Безопасность бэкенда|7.4 Безопасность бэкенда]] · → [[BE 7.4.2 Инъекции — SQL, командные, LDAP, десериализация|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->





























> [!info] Зачем это на собесе
> Стандартный вопрос: «какие уязвимости API вы знаете и как от них защищаетесь».

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

OWASP API Security Top 10 (редакция 2023):

| # | Риск | Защита |
|---|---|---|
| API1 | Broken Object Level Authorization (BOLA/IDOR) | проверка доступа к каждому объекту по владельцу |
| API2 | Broken Authentication | стойкие пароли, MFA, короткие токены, защита от перебора |
| API3 | Broken Object Property Level Authorization | не отдавать и не принимать лишние поля (DTO, allowlist) |
| API4 | Unrestricted Resource Consumption | лимиты запросов, размеров, пагинации, таймауты |
| API5 | Broken Function Level Authorization | проверка ролей/политик на функциях (админские методы) |
| API6 | Unrestricted Access to Sensitive Business Flows | защита сценариев (покупка, регистрация) от автоматизации |
| API7 | Server Side Request Forgery (SSRF) | allowlist адресов, запрет внутренних сетей, отдельная сеть |
| API8 | Security Misconfiguration | безопасные настройки, отключённые отладочные возможности, актуальные заголовки |
| API9 | Improper Inventory Management | реестр всех API и версий, вывод старых из эксплуатации |
| API10 | Unsafe Consumption of APIs | проверка данных от сторонних API как недоверенных |

```csharp
// BOLA: проверка владельца на уровне запроса
var order = await db.Orders.FirstOrDefaultAsync(o => o.Id == id && o.OwnerId == user.Id, ct);
return order is null ? Results.NotFound() : Results.Ok(order.ToDto());
```

Практики: единая авторизация как политика по умолчанию (deny by default), security-заголовки (HSTS, X-Content-Type-Options), CORS с allowlist, логирование попыток доступа, зависимости на сканировании (SCA), SAST/DAST в CI.

## Нюансы и подводные камни

- Самая частая проблема — BOLA: авторизацию проверяют только на уровне роли.
- Mass assignment: биндинг тела в сущность.
- Обход через смену метода/версии API/пути.
- Информация в ошибках (стек, SQL) помогает атакующему.
- Безопасность нельзя добавить в конце: моделирование угроз на проектировании.

## Практика

1. Проверьте свои эндпоинты на BOLA: запросите чужой ресурс.
2. Добавьте лимиты и максимальные размеры запросов.
3. Включите dependency scanning (`dotnet list package --vulnerable`).

## Вопросы с ответами

> [!question]- Что такое BOLA/IDOR?
> Доступ к чужому объекту подменой идентификатора из-за отсутствия проверки владельца.

> [!question]- Что такое SSRF?
> Атака, когда сервер делает запросы по адресу, заданному атакующим (в том числе к внутренней сети или метаданным облака).

## Связанные темы

- [[N:3ea331048679813d96e3e4f7c0faab14]]
- [[N:3ea3310486798151bdfce23ff2d8a287]]
