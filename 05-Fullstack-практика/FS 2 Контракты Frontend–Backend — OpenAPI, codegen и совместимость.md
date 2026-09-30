---
type: topic
domain: fullstack
stage: 0
order: 2
notion_id: 43d95ed2c4eb430f9e3a8327da318ff1
status: todo
level: middle+
tags: [domain/fullstack, kind/project, level/middle+, priority/should]
priority: should
time: 10
---

# Контракты Frontend–Backend: OpenAPI, codegen и совместимость

↑ [[FS Fullstack-практика]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~10 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Контракт API — граница между командами: от него зависят совместимость, скорость разработки и количество багов интеграции.

## Цель

Сделать **OpenAPI единым источником истины** для взаимодействия Frontend и Backend: спроектировать контракт (API-first), сгенерировать серверные заглушки/клиента, автоматически проверять совместимость и договориться о правилах изменений (версионирование, депрекейшн).

## API-first

1. Сначала проектируем контракт (`openapi.yaml`) совместно (frontend + backend + QA).
2. Из контракта: **mock-сервер** для фронтенда (Prism/MSW), валидация реализации, **кодогенерация** клиента и DTO.
3. Backend реализует контракт, фронтенд работает по моку параллельно.
4. CI проверяет: спецификация валидна, реализация ей соответствует, **нет breaking changes**.

Альтернатива **code-first**: контракт генерируется из кода (Swashbuckle/NSwag/`Microsoft.AspNetCore.OpenApi`) — быстрее, но риск «случайных» изменений API; решается снапшотом спецификации в репозитории и проверкой diff в CI.

## Пример спецификации

```yaml
openapi: 3.1.0
info: { title: Clinic API, version: 1.3.0 }
servers: [{ url: https://clinic.example.com/api/v1 }]
security: [{ oidc: [] }]
paths:
  /doctors:
    get:
      operationId: listDoctors
      tags: [Catalog]
      parameters:
        - { name: specialtyId, in: query, schema: { type: integer } }
        - { name: cursor, in: query, schema: { type: string } }
        - { name: limit, in: query, schema: { type: integer, minimum: 1, maximum: 100, default: 20 } }
      responses:
        "200": { description: OK, content: { application/json: { schema: { $ref: "#/components/schemas/DoctorPage" } } } }
  /appointments:
    post:
      operationId: createAppointment
      tags: [Appointments]
      parameters:
        - { name: Idempotency-Key, in: header, required: true, schema: { type: string, format: uuid } }
      requestBody:
        required: true
        content: { application/json: { schema: { $ref: "#/components/schemas/CreateAppointment" } } }
      responses:
        "201": { description: Создано, content: { application/json: { schema: { $ref: "#/components/schemas/Appointment" } } } }
        "400": { $ref: "#/components/responses/ValidationProblem" }
        "409": { description: Слот уже занят, content: { application/problem+json: { schema: { $ref: "#/components/schemas/Problem" } } } }
components:
  securitySchemes:
    oidc: { type: openIdConnect, openIdConnectUrl: https://clinic.example.com/auth/realms/clinic/.well-known/openid-configuration }
  schemas:
    CreateAppointment:
      type: object
      required: [slotId]
      properties: { slotId: { type: integer, format: int64 }, comment: { type: string, maxLength: 500 } }
    Appointment:
      type: object
      required: [id, slotId, status, startsAt]
      properties:
        id: { type: integer, format: int64 }
        slotId: { type: integer, format: int64 }
        status: { type: string, enum: [booked, confirmed, cancelled, completed, no_show] }
        startsAt: { type: string, format: date-time }
    Problem:                                   # RFC 9457 (Problem Details)
      type: object
      properties: { type: { type: string }, title: { type: string }, status: { type: integer }, detail: { type: string }, traceId: { type: string } }
```

## Принципы дизайна API

- **ресурсы и глаголы**: существительные во множественном числе, HTTP-методы по смыслу, корректные коды (201, 204, 400, 401, 403, 404, 409, 422, 429);
- **ошибки единым форматом** — **Problem Details (RFC 9457)** с `traceId` для корреляции с логами;
- **пагинация**: cursor (для лент/активных данных) или offset + лимиты; единый формат ответа;
- **фильтрация/сортировка** параметрами, **валидация** на границе (схема + FluentValidation);
- **идемпотентность** записи: заголовок `Idempotency-Key` для POST (повтор возвращает тот же результат);
- **конкурентность**: `ETag`/`If-Match` или поле `version` для оптимистичных обновлений (412/409 при конфликте);
- **время**: ISO 8601 UTC (`date-time`), часовые пояса на стороне клиента;
- **деньги/числа**: точные типы (string/decimal), идентификаторы — непрозрачные;
- **безопасность**: OIDC Bearer, scopes/роли, минимальные данные в ответах, не раскрывать внутренности в ошибках;
- **rate limits**: заголовки `Retry-After`, `RateLimit-*`;
- **HATEOAS** — по необходимости (обычно не нужен); **GraphQL/gRPC** — другие варианты контракта для других сценариев.

## Кодогенерация

**Клиент TypeScript** для Vue:

```bash
npx openapi-typescript openapi.yaml -o web/src/api/schema.d.ts        # типы
# или полноценный клиент:
npx @hey-api/openapi-ts -i openapi.yaml -o web/src/api/client
# Orval: сгенерирует клиент + хуки TanStack Query + MSW-моки
```

```ts
import createClient from 'openapi-fetch'
import type { paths } from './schema'
export const api = createClient<paths>({ baseUrl: '/api/v1' })

const { data, error } = await api.POST('/appointments', {
  body: { slotId: 42 },
  params: { header: { 'Idempotency-Key': crypto.randomUUID() } },
})
```

**Сервер (.NET)**: NSwag/Kiota для DTO и клиентов, `Microsoft.AspNetCore.OpenApi` + `Scalar/Swagger UI` для документации; **контрактные тесты** проверяют соответствие ответов схеме (Schemathesis, Dredd, `Microsoft.AspNetCore.Mvc.Testing` + валидатор схем).

Правила: сгенерированные файлы — в Git или генерируются в CI (но единообразно); не править руками; версия генератора зафиксирована; клиент упаковывается как пакет при нескольких потребителях.

## Mock и параллельная разработка

**Prism** (`prism mock openapi.yaml`) или **MSW** с примерами из спецификации: фронтенд разрабатывает UI до готовности backend; одинаковые моки в Storybook и e2e; примеры (`examples`) в спецификации — «живая документация».

## Совместимость и версионирование

**Правила обратной совместимости** (можно без новой версии):

- добавление **необязательных** полей ответа и параметров запроса;
- добавление новых эндпоинтов, новых значений enum **только если клиенты терпимы** (tolerant reader);
- расширение допустимых значений.

**Breaking changes** (требуют новой версии/миграции):

- удаление/переименование полей, эндпоинтов, значений enum;
- изменение типа или формата поля, обязательности, семантики, кодов ошибок;
- ужесточение валидации.

Инструменты проверки: **oasdiff** (`oasdiff breaking old.yaml new.yaml` в CI падает на breaking), **Optic**, **Spectral** (линтер правил стиля), Redocly.

```yaml
contract-check:
  stage: test
  script:
    - npx @stoplight/spectral-cli lint openapi.yaml
    - oasdiff breaking origin/main:openapi.yaml openapi.yaml --fail-on ERR
    - npx openapi-typescript openapi.yaml -o /tmp/schema.d.ts && diff -q /tmp/schema.d.ts web/src/api/schema.d.ts
```

**Версионирование API**: в пути (`/api/v1`), заголовком или медиа-типом; новая мажорная версия — только при необходимости; **депрекейшн**: заголовки `Deprecation`, `Sunset`, документация, срок поддержки (например, 6 мес), метрики использования старой версии перед удалением.

**Expand and contract** для изменений: добавить новое поле → клиенты переходят → удалить старое в следующей версии. Совместимость **во времени выкатки**: при rolling update одновременно работают версии API v(N) и v(N+1); фронтенд может быть старее/новее бэкенда (кэш, долгоживущие вкладки) → поддерживать **окно совместимости** и порядок выкатки (сначала backend с обратной совместимостью, потом frontend).

## События и асинхронные контракты

События (уведомления, интеграции) описываются **AsyncAPI** / JSON Schema / Avro + **Schema Registry**; правила совместимости (backward/forward/full); версия в типе события; потребители толерантны к новым полям.

## Тестирование контракта

- **провайдер**: сервер проходит валидацию по схеме (Schemathesis генерирует запросы по спецификации, ищет 5xx и несоответствия);
- **потребитель**: Pact (consumer-driven contracts) — фронтенд/сервис публикует ожидания, бэкенд проверяет;
- **e2e-сценарии** на staging (Playwright) как последняя линия;
- снапшот `openapi.yaml` в репозитории, проверка diff в PR, автоматическая публикация документации.

## Документация и DX

Swagger UI/Scalar/Redoc, примеры запросов (curl, `.http`), Postman-коллекция из OpenAPI, changelog API, руководство «как добавить эндпоинт» (процесс: спецификация → ревью → моки → реализация).

## Что делаем

- [ ] Спроектировать `openapi.yaml` для каталога и записей (API-first), единый формат ошибок Problem Details;
- [ ] Настроить Spectral-правила стиля и проверку в CI;
- [ ] Сгенерировать TypeScript-клиент (openapi-typescript/Orval) и подключить в SPA;
- [ ] Поднять mock (Prism/MSW) для фронтенда;
- [ ] Добавить `oasdiff breaking` в пайплайн; описать политику версий и депрекейшна;
- [ ] Контрактные тесты (Schemathesis/Pact) и проверка ответов схеме;
- [ ] Идемпотентность (`Idempotency-Key`) и оптимистичные блокировки (`ETag`/`version`) в контракте;
- [ ] Документация (Scalar/Redoc) публикуется из CI.

## Результат / артефакты

- `api/openapi.yaml`, правила `.spectral.yaml`;
- сгенерированный клиент `web/src/api/*` (+ скрипт генерации в `package.json`/Makefile);
- CI-джоба contract-check; политика версионирования и депрекейшна (`docs/api-versioning.md`);
- mock-окружение для frontend; набор контрактных тестов;
- опубликованная документация API.

## Что рассказать на собесе

- почему API-first: параллельная разработка, единый источник истины, меньше интеграционных багов;
- какие изменения считаются breaking и как вы это автоматически ловите (oasdiff, контрактные тесты);
- как обеспечена совместимость при rolling update и разной скорости выкатки фронта/бэка;
- как спроектирована идемпотентность и конкурентные обновления;
- как организованы версии и депрекейшн публичного API.
