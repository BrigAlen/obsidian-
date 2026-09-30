---
type: topic
domain: frontend
stage: 7
section: "7.3"
order: 6
status: todo
level: senior
notion_id: 3ea3310486798182915ffb9e0bd92f62
tags: [domain/frontend, stage/7, level/senior, topic/security, topic/npm, topic/supply-chain, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Уязвимости зависимостей и npm audit

↑ [[FE 7.3 Безопасность фронтенда|7.3 Безопасность фронтенда]] · ← [[FE 7.3.5 Безопасное хранение токенов|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Большая часть кода в проекте — чужая. Спрашивают, как вы управляете цепочкой поставок.

## Риски

- известные CVE в пакетах;
- **typosquatting** (похожее имя пакета);
- захваченные аккаунты мейнтейнеров, вредоносные обновления;
- вредоносные `postinstall`-скрипты;
- **dependency confusion** (приватное имя публикуется в публичном реестре).

## Инструменты

```sh
npm audit                    # известные уязвимости
npm audit --omit=dev         # только прод-зависимости
npm audit fix                # безопасные обновления
npm ci                       # строго по lock-файлу
npm outdated                 # устаревшие пакеты
```

Дополнительно: **Dependabot**, **Renovate** (автоматические PR), **Snyk**, **OWASP Dependency-Check**, **Socket.dev**, OSV-Scanner.

## Практики

- **lock-файл в репозитории** и `npm ci` в CI;
- фиксировать версии, обновления пачками через PR с прогоном тестов;
- `--ignore-scripts` или `ignore-scripts=true` в `.npmrc` (включать выборочно);
- проверять новые зависимости: активность, число загрузок, лицензия, размер;
- минимум зависимостей: «нужна ли библиотека ради одной функции»;
- SRI (`integrity`) для скриптов с CDN;
- проверка лицензий (`license-checker`);
- SBOM (CycloneDX) для требований безопасности;
- npm provenance и подписи.

```html
<script src="https://cdn.example.com/lib.js"
        integrity="sha384-..." crossorigin="anonymous"></script>
```

## Нюансы

- `npm audit` шумит по dev-зависимостям и недостижимым путям: оценивайте эксплуатируемость;
- транзитивные зависимости чинят через `overrides` (npm) или `resolutions` (yarn).

## Вопросы с ответами

> [!question]- Как защититься от атак через зависимости?
> Lock-файл и `npm ci`, автоматические обновления с ревью, аудит в CI, отключение install-скриптов, SRI для CDN, минимум зависимостей.

> [!question]- Что делать, если уязвимость в транзитивной зависимости, а патча нет?
> Проверить достижимость, обновить родителя, применить `overrides` на исправленную версию, при отсутствии фикса — заменить пакет или ограничить использование.
