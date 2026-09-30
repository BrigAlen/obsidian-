---
type: topic
domain: devops
stage: 8
order: 5
status: todo
level: senior
tags: [domain/devops, stage/8, level/senior, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 9
---

# Keycloak в инфраструктуре: развёртывание, realm-импорт, темы, БД

↑ [[DO Этап 8 · Senior — надёжность, безопасность, платформа|Этап 8 · Senior: надёжность, безопасность, платформа]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~9 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Keycloak — центр аутентификации в вашем стеке. Нужно уметь развернуть его, автоматизировать конфигурацию и эксплуатировать.

## Что это

**Keycloak** — open-source Identity and Access Management: SSO, **OIDC/OAuth 2.0**, **SAML 2.0**, федерация (LDAP/AD, внешние IdP: Google, GitHub), MFA, управление пользователями, роли/группы, токены, **Admin API**. Основные сущности:

| Сущность | Описание |
|---|---|
| **Realm** | изолированное пространство: пользователи, клиенты, роли, настройки (master — служебный; прикладные realm отдельно) |
| **Client** | приложение, использующее Keycloak (SPA — public + PKCE; backend API — confidential/bearer-only; сервис-сервис — service account) |
| **User / Group / Role** | пользователи, группы, realm- и client-роли |
| **Identity Provider** | внешние поставщики идентичности |
| **User Federation** | LDAP/Kerberos |
| **Client scopes / mappers** | какие claims попадают в токены |
| **Authentication flows** | сценарии входа: пароль, OTP, WebAuthn, условия |
| **Events / Admin events** | аудит входов и изменений |

Токены: **access token** (JWT, короткий TTL), **refresh token**, **ID token**; проверка подписи по JWKS (`/realms/{realm}/protocol/openid-connect/certs`). Well-known: `/realms/{realm}/.well-known/openid-configuration`.

## Развёртывание (Quarkus-версия, 17+)

Контейнер `quay.io/keycloak/keycloak`; режимы: `start-dev` (разработка: H2, HTTP) и `start` (**production**: нужны настроенный hostname, TLS/прокси и внешняя БД). Команда `kc.sh build` (оптимизация) и `start --optimized`.

```yaml
# compose.yaml (фрагмент)
services:
  keycloak:
    image: quay.io/keycloak/keycloak:26.0
    command: ["start", "--optimized", "--import-realm"]          # --import-realm импортирует /opt/keycloak/data/import/*.json
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://db:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD_FILE: /run/secrets/kc_db_password
      KC_HOSTNAME: https://auth.example.com
      KC_HTTP_ENABLED: "true"                # TLS терминируется на прокси
      KC_PROXY_HEADERS: xforwarded           # доверять X-Forwarded-* от reverse proxy
      KC_HEALTH_ENABLED: "true"
      KC_METRICS_ENABLED: "true"
      KC_BOOTSTRAP_ADMIN_USERNAME: admin
      KC_BOOTSTRAP_ADMIN_PASSWORD_FILE: /run/secrets/kc_admin_password      # временный админ, сразу создать постоянного и удалить
    volumes:
      - ./realm-export:/opt/keycloak/data/import:ro
      - ./themes:/opt/keycloak/themes:ro
    depends_on: { db: { condition: service_healthy } }
    healthcheck: { test: ["CMD-SHELL", "exec 3<>/dev/tcp/localhost/9000; echo -e 'GET /health/ready HTTP/1.1\\r\\nhost: localhost\\r\\nConnection: close\\r\\n\\r\\n' >&3; grep -q '\"UP\"' <&3"], interval: 15s, retries: 10, start_period: 30s }
```

Nginx перед Keycloak: HTTPS, заголовки `X-Forwarded-For/Proto/Host/Port`, **увеличенные буферы** для больших cookie/токенов (`proxy_buffer_size 128k; proxy_buffers 4 256k`), закрыть админ-консоль (`/admin`) и `/metrics`, `/health` от внешнего доступа (по IP/VPN).

Kubernetes: **Keycloak Operator** (CRD `Keycloak`, `KeycloakRealmImport`), Helm-чарты (Bitnami — не для прод без проверки, codecentric keycloakx), StatefulSet/Deployment ≥ 2 реплики с **Infinispan** (распределённый кэш: режим `kubernetes` discovery `jdbc-ping`/DNS ping), Ingress с TLS, PDB, ресурсы (JVM: 1–2 ГБ+ памяти), health/metrics.

## База данных

Продакшн: **PostgreSQL** (внешний, с репликацией и бэкапами) — не встроенная H2. Отдельная БД/пользователь, пулы соединений (`KC_DB_POOL_*`), регулярные бэкапы (содержит пользователей, хэши паролей, конфигурацию), тест восстановления, миграции схемы происходят **автоматически при обновлении** версии (бэкап перед апгрейдом!). Оценка: рост таблиц событий (`EVENT_ENTITY`, `ADMIN_EVENT_ENTITY`) — TTL/очистка, `KC_SPI_EVENTS_STORE_...expiration`.

## Realm-импорт и автоматизация конфигурации

Конфигурация — **код**, а не клики:

- **Импорт realm JSON** при старте: `--import-realm` (файлы в `data/import`; импортируется только если realm **ещё не существует**) или `kc.sh import --dir`; экспорт: `kc.sh export --dir /tmp/export --realm clinic`, либо Admin-консоль «Partial export» (секреты клиентов и пароли **не** экспортируются по умолчанию);
- **KeycloakRealmImport** CRD (Operator);
- **Terraform provider** `mrparkers/keycloak` (→ `keycloak/keycloak`): realm, clients, roles, groups, flows, mappers — декларативно, идемпотентно, с drift-контролем (предпочтительно для долгой жизни);
- **keycloak-config-cli** (adorsys): применение YAML/JSON конфигурации с обновлением существующего realm;
- **Admin REST API** / `kcadm.sh`: скрипты bootstrap;
- подстановка переменных/секретов в импорт (`${ENV_VAR}` поддерживается в realm JSON при `--import-realm` через переменные окружения) — секреты клиентов не хранить в репозитории открыто; брать из Vault/Secrets.

```json
{
  "realm": "clinic",
  "enabled": true,
  "sslRequired": "external",
  "registrationAllowed": false,
  "loginWithEmailAllowed": true,
  "bruteForceProtected": true,
  "accessTokenLifespan": 300,
  "ssoSessionIdleTimeout": 1800,
  "roles": { "realm": [{ "name": "doctor" }, { "name": "admin" }] },
  "clients": [
    { "clientId": "clinic-web", "publicClient": true, "standardFlowEnabled": true, "directAccessGrantsEnabled": false,
      "redirectUris": ["https://app.example.com/*"], "webOrigins": ["https://app.example.com"],
      "attributes": { "pkce.code.challenge.method": "S256" } },
    { "clientId": "clinic-api", "bearerOnly": true },
    { "clientId": "clinic-worker", "serviceAccountsEnabled": true, "secret": "${CLINIC_WORKER_SECRET}" }
  ]
}
```

## Темы и кастомизация

**Themes** (login, account, admin, email, welcome): FreeMarker-шаблоны + CSS + i18n (`messages_ru.properties`), размещаются в `/opt/keycloak/themes/<name>` (образ или том); `parent=keycloak.v2`; переопределяйте минимум (CSS/логотип/сообщения), чтобы легче обновляться; тестировать при апгрейде версий. Также: **SPI-расширения** (кастомные аутентификаторы, mappers, event listeners) в виде JAR в `providers/` с пересборкой (`kc.sh build`); Keycloakify (React-темы).

## Безопасность

- **hostname и TLS** правильно настроены (issuer в токенах зависит от hostname: несовпадение ломает валидацию у API);
- админ-консоль только из внутренней сети/VPN, MFA для админов, отдельный постоянный администратор, отключить/удалить временного;
- политики паролей, **brute-force detection**, MFA (OTP/WebAuthn), ограничение регистраций, подтверждение email, **captcha**;
- **клиенты**: SPA — **Authorization Code + PKCE**, без implicit/password; строгие `redirectUris` (без `*` в домене), `webOrigins`; минимальные scopes; короткие access-токены (5–15 мин), refresh rotation; секреты confidential-клиентов в Vault;
- валидация токенов в API: подпись (JWKS), `iss`, `aud`, `exp`, scope/roles; ключи ротируются (Realm keys);
- хранение: шифрование БД/бэкапов, минимум прав БД-пользователя;
- **аудит**: events (LOGIN, LOGIN_ERROR, LOGOUT), admin events → в Loki/ClickHouse/SIEM;
- обновления безопасности (CVE), регулярные апгрейды версий; ограничение выхода в сеть;
- защита эндпоинтов `/metrics`, `/health`, `/admin`, `/realms/master` от публичного доступа.

## Эксплуатация

- **HA**: ≥ 2 реплики, общий Infinispan-кластер (сессии в кэше; при потере всех узлов сессии теряются, если не persistent sessions — в новых версиях включены), LB (sticky не обязателен в современных версиях), PDB;
- **производительность**: JVM heap (`JAVA_OPTS_KC_HEAP`), пул БД, кэши, хэширование паролей (PBKDF2 итерации — баланс защиты и CPU), нагрузочные тесты логинов;
- **метрики**: `/metrics` (Micrometer) → Prometheus: логины, ошибки, JVM, БД-пул; `KC_HEALTH_ENABLED` для probes; дашборды Grafana, алерты на недоступность и рост ошибок входа;
- **логи**: JSON (`KC_LOG_CONSOLE_OUTPUT=json`), уровень, аудит-события;
- **бэкапы**: БД (pg_dump/PITR) + экспорт конфигурации (Terraform/realm JSON в Git); DR-план; тест восстановления;
- **апгрейды**: читать миграционные заметки (breaking changes между мажорами), бэкап, сначала staging; blue/green с одной БД невозможен без миграций — осторожно;
- **зависимость**: Keycloak критичен для входа всех систем: доступность, кэширование JWKS в API (не запрашивать на каждый запрос), обработка недоступности, токены живут до истечения;
- **мультитенантность**: realm на тенанта (дорого при сотнях) или organizations (новые версии);
- **интеграции**: nginx/ingress + oauth2-proxy для приложений без поддержки OIDC, Grafana/ArgoCD/Kubernetes API через OIDC, Vault OIDC/JWT.

## Типичные проблемы

| Симптом | Причина |
|---|---|
| Ошибки `Invalid issuer` в API | `KC_HOSTNAME` не совпадает с URL, по которому получены токены; внутренний и внешний адреса |
| Бесконечные редиректы/«mixed content» | неверные proxy-заголовки/`KC_PROXY_HEADERS`, HTTP/HTTPS |
| 502/«upstream sent too big header» | большие cookie/токены: буферы nginx |
| `Invalid redirect URI` | `redirectUris` клиента не совпадают |
| После рестарта пропали настройки | `--import-realm` не перезаписывает существующий realm; конфигурация не в коде; БД не сохранена (dev-режим H2) |
| Медленные логины | PBKDF2-итерации, нехватка CPU, БД, недоступный LDAP |
| Сессии пропадают при смене узла | Infinispan не кластеризован (discovery) |

## Вопросы с ответами

> [!question]- Как автоматизировать конфигурацию Keycloak?
> Хранить конфигурацию как код: импорт realm JSON (`--import-realm`/Operator CRD) для bootstrap, Terraform provider или keycloak-config-cli для идемпотентного применения изменений, секреты — из Vault/секретов окружения.

> [!question]- Какие настройки критичны для продакшн-запуска Keycloak за nginx?
> Внешняя PostgreSQL, корректные `hostname` и proxy-заголовки (`KC_PROXY_HEADERS`), TLS на прокси, увеличенные буферы для cookie/токенов, закрытая админ-консоль, health/metrics, несколько реплик с Infinispan, бэкапы и мониторинг.

> [!question]- Как безопасно настроить SPA-клиент?
> Public client с Authorization Code + PKCE, строгие redirect URI и web origins, короткий срок access-токена, без implicit и password grant.
