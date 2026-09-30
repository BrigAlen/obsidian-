---
type: domain
domain: devops
tags: [domain/devops, kind/moc]
---

# DevOps

Linux, Docker, CI/CD, Nginx, Kubernetes, Ansible, Terraform, observability, безопасность.

↑ [[00 Карта]]

> [!tip] Как проходить
> Этапы по порядку → внутри этапа разделы по порядку. После каждой темы: карточки → квиз → перенос в статус `done`.

## Этапы
- [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]
- [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]
- [[DO Этап 3 · CI-CD|Этап 3 · CI-CD]]
- [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]
- [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]
- [[DO Этап 6 · Infrastructure as Code — Ansible, Terraform|Этап 6 · Infrastructure as Code: Ansible, Terraform]]
- [[DO Этап 7 · Observability и эксплуатация|Этап 7 · Observability и эксплуатация]]
- [[DO Этап 8 · Senior — надёжность, безопасность, платформа|Этап 8 · Senior: надёжность, безопасность, платформа]]
- [[DO Этап 9 · Собес Middle DevOps — вопросы, практика, деплой систем|Этап 9 · Собес Middle DevOps: вопросы, практика, деплой систем]]

## Прогресс
```dataview
TABLE WITHOUT ID stage AS Этап, length(rows) AS Всего, length(filter(rows, (r) => r.status = "done")) AS Готово
FROM "04-DevOps"
WHERE type = "topic"
GROUP BY stage
SORT stage ASC
```
