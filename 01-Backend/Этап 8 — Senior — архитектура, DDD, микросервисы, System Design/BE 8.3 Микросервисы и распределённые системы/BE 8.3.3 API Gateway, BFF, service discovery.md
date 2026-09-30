---
type: topic
domain: backend
stage: 8
section: "8.3"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981cfa283cc1de55bd7d1
tags: [domain/backend, stage/8, level/senior, topic/microservices, topic/gateway, topic/bff, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# API Gateway, BFF, service discovery

↑ [[BE 8.3 Микросервисы и распределённые системы|8.3 Микросервисы и распределённые системы]] · ← [[BE 8.3.2 Декомпозиция сервисов и database per service|Предыдущая]] · → [[BE 8.3.4 Синхронное и асинхронное взаимодействие сервисов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


























> [!info] Зачем это на собесе
> Как клиенты обращаются к десяткам сервисов и что делает шлюз.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**API Gateway** — единая точка входа: маршрутизация, аутентификация, лимиты, TLS, кэш, агрегация, трансформации, наблюдаемость.

| Технология | Заметки |
|---|---|
| YARP (.NET) | программируемый reverse proxy, гибкость кода |
| Ocelot | шлюз для .NET |
| Envoy / Nginx / Traefik / Kong | универсальные прокси/шлюзы |
| Облачные (AWS API Gateway, Azure APIM) | управляемые |

```json
{ "ReverseProxy": {
  "Routes": { "orders": { "ClusterId": "orders", "Match": { "Path": "/api/orders/{**rest}" } } },
  "Clusters": { "orders": { "Destinations": { "d1": { "Address": "http://orders:8080/" } }, "LoadBalancingPolicy": "RoundRobin" } } } }
```

**BFF (Backend For Frontend)** — отдельный слой под конкретного клиента (web, mobile), собирающий и упрощающий данные под его экраны; у каждого клиента свой BFF.

| Задача | Gateway | BFF |
|---|---|---|
| Маршрутизация, лимиты, TLS | да | нет |
| Общая аутентификация | да | использует |
| Агрегация под экран | нет (или минимально) | да |
| Логика клиента | нет | да |

**Service discovery** — как сервисы находят друг друга: DNS Kubernetes (`orders.default.svc`), реестры (Consul, Eureka), клиентская балансировка. В Kubernetes достаточно Service и DNS.

## Нюансы и подводные камни

- Шлюз не место для бизнес-логики: он не должен стать новым монолитом.
- Единая точка отказа: репликация и мониторинг.
- Агрегация в шлюзе увеличивает задержку и связанность.
- Сквозные заголовки (`traceparent`, `Authorization`) должны корректно пробрасываться.
- Аутентификация в шлюзе не отменяет авторизацию в сервисах (zero trust).

## Практика

1. Настройте YARP маршрутизацию на два сервиса с health checks.
2. Реализуйте BFF для веб-клиента, агрегирующий 3 сервиса.
3. Добавьте rate limiting и JWT-проверку на шлюзе.

## Вопросы с ответами

> [!question]- Зачем API Gateway?
> Единая точка входа для клиентов: маршрутизация, безопасность, ограничения, наблюдаемость.

> [!question]- Чем BFF отличается от gateway?
> BFF настроен под конкретного клиента и агрегирует данные для его интерфейса; gateway — общий инфраструктурный слой.

## Связанные темы

- [[N:3ea33104867981f789c6c296ce694c5b]]
- [[N:3ea33104867981a697b2ca3e5ba807ec]]
