---
type: topic
domain: fullstack
stage: 0
order: 3
notion_id: c4c0cab0ccb74e4cb2fff9db2842ea35
status: todo
level: middle+
tags: [domain/fullstack, kind/project, level/middle+, priority/should]
priority: should
time: 13
---

# Реализация вертикального среза Vue 3 + ASP.NET Core + PostgreSQL

↑ [[FS Fullstack-практика]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~13 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Вертикальный срез (от UI до БД) — лучший способ показать умение доводить функциональность до рабочего состояния через все слои.

## Цель

Реализовать **один полный сценарий** «Запись на приём» по всем слоям: Vue 3 SPA → ASP.NET Core API → PostgreSQL, с авторизацией, валидацией, обработкой конкурентности, тестами и асинхронным уведомлением.

**Вертикальный срез** (vertical slice) — тонкая, но рабочая функциональность, проходящая через все уровни (UI, API, бизнес-логика, хранилище, инфраструктура), в отличие от «горизонтальной» разработки слоями. Даёт ранний feedback и проверяет архитектуру.

## Сценарий

1. Пациент входит через Keycloak.
2. Открывает каталог врачей, выбирает врача и видит свободные слоты на неделю.
3. Нажимает «Записаться» → запрос `POST /appointments` с `Idempotency-Key`.
4. Сервер транзакционно бронирует слот, создаёт запись и событие в outbox.
5. Worker отправляет уведомление; пациент видит запись в «Мои записи» и может отменить.

## База данных (PostgreSQL)

```sql
CREATE TABLE slots (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  doctor_id   bigint NOT NULL REFERENCES doctors(id),
  starts_at   timestamptz NOT NULL,
  duration    smallint NOT NULL DEFAULT 20,
  status      text NOT NULL DEFAULT 'free' CHECK (status IN ('free','booked','blocked')),
  UNIQUE (doctor_id, starts_at)
);
CREATE INDEX idx_slots_doctor_time ON slots (doctor_id, starts_at) WHERE status = 'free';

CREATE TABLE appointments (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  slot_id     bigint NOT NULL REFERENCES slots(id),
  patient_id  bigint NOT NULL REFERENCES patients(id),
  status      text NOT NULL DEFAULT 'booked',
  version     integer NOT NULL DEFAULT 1,
  created_at  timestamptz NOT NULL DEFAULT now()
);
-- инвариант: один слот — одна активная запись
CREATE UNIQUE INDEX uq_active_appointment_slot ON appointments (slot_id) WHERE status IN ('booked','confirmed');

CREATE TABLE idempotency_keys (key uuid PRIMARY KEY, user_sub text NOT NULL, response jsonb, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE outbox (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, type text NOT NULL, payload jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), published_at timestamptz);
CREATE INDEX idx_outbox_unpublished ON outbox (id) WHERE published_at IS NULL;
```

Миграции — EF Core (`dotnet ef migrations add`) или Flyway; обратно совместимые, применяются отдельным шагом деплоя.

## Backend (ASP.NET Core)

Структура: `Domain` (сущности, правила) → `Application` (use cases, валидация) → `Infrastructure` (EF Core, внешние сервисы) → `Api` (эндпоинты).

```csharp
// Application: команда бронирования
public sealed record BookAppointment(long SlotId, string UserSub, Guid IdempotencyKey);

public sealed class BookAppointmentHandler(ClinicDbContext db, TimeProvider clock)
{
    public async Task<Result<AppointmentDto>> Handle(BookAppointment cmd, CancellationToken ct)
    {
        // 1. идемпотентность: повтор возвращает прежний ответ
        var saved = await db.IdempotencyKeys.FindAsync([cmd.IdempotencyKey], ct);
        if (saved is not null) return Result.Ok(saved.Response.Deserialize<AppointmentDto>()!);

        await using var tx = await db.Database.BeginTransactionAsync(IsolationLevel.ReadCommitted, ct);

        var patient = await db.Patients.SingleAsync(p => p.UserSub == cmd.UserSub, ct);

        // 2. атомарное занятие слота (условие в UPDATE защищает от гонок)
        var affected = await db.Slots
            .Where(s => s.Id == cmd.SlotId && s.Status == SlotStatus.Free && s.StartsAt > clock.GetUtcNow())
            .ExecuteUpdateAsync(s => s.SetProperty(x => x.Status, SlotStatus.Booked), ct);
        if (affected == 0) return Result.Conflict("Слот недоступен");

        var appt = new Appointment(cmd.SlotId, patient.Id);
        db.Appointments.Add(appt);
        db.Outbox.Add(OutboxMessage.Create("appointment.booked", new { appt.Id, patient.Id, cmd.SlotId }));

        try { await db.SaveChangesAsync(ct); }
        catch (DbUpdateException e) when (e.IsUniqueViolation()) { return Result.Conflict("Слот уже занят"); }   // страховка уникальным индексом

        var dto = appt.ToDto();
        db.IdempotencyKeys.Add(new(cmd.IdempotencyKey, cmd.UserSub, JsonSerializer.SerializeToDocument(dto)));
        await db.SaveChangesAsync(ct);
        await tx.CommitAsync(ct);
        return Result.Ok(dto);
    }
}
```

```csharp
// Api: эндпоинт
app.MapPost("/api/v1/appointments", async (CreateAppointmentRequest req, [FromHeader(Name = "Idempotency-Key")] Guid key,
        ClaimsPrincipal user, BookAppointmentHandler h, CancellationToken ct) =>
    (await h.Handle(new(req.SlotId, user.FindFirstValue("sub")!, key), ct)).ToHttpResult())
   .RequireAuthorization("patient")
   .AddEndpointFilter<ValidationFilter<CreateAppointmentRequest>>()
   .WithName("createAppointment");
```

Ключевые элементы:

- **авторизация**: JWT Bearer (Keycloak), `AddAuthentication().AddJwtBearer` с `Authority`, `Audience`; политики по ролям; пациент видит **только свои** записи (фильтр по `sub` на уровне запросов);
- **валидация**: FluentValidation/Minimal API filters → `ProblemDetails` 400/422;
- **конкурентность**: условное обновление + уникальный индекс (никаких «SELECT, затем UPDATE» без защиты); повтор при `40001`/serialization;
- **идемпотентность**: таблица ключей (TTL-очистка);
- **outbox**: событие записывается в той же транзакции; **Worker** читает необработанные (`FOR UPDATE SKIP LOCKED`), публикует, помечает;
- **обработка ошибок**: глобальный `ExceptionHandler` → Problem Details с `traceId`; логирование без ПДн;
- **производительность**: `AsNoTracking` для чтения, проекции, индексы, пагинация cursor, кэш каталога (Redis, cache-aside с jitter TTL), пул соединений;
- **health checks** (`/health/live`, `/health/ready`), graceful shutdown, OpenTelemetry (трассы, метрики `appointments_booked_total`).

### Worker (outbox)

```csharp
while (!ct.IsCancellationRequested)
{
    var batch = await db.Database.SqlQuery<OutboxRow>($"""
        SELECT id, type, payload FROM outbox WHERE published_at IS NULL ORDER BY id LIMIT 50 FOR UPDATE SKIP LOCKED
        """).ToListAsync(ct);                       // внутри транзакции
    foreach (var m in batch) { await bus.PublishAsync(m, ct); await MarkPublished(m.Id, ct); }
    await Task.Delay(batch.Count == 0 ? 1000 : 0, ct);
}
```

Потребитель уведомлений идемпотентен (дедупликация по `event_id`), ретраи с backoff, dead-letter очередь.

## Frontend (Vue 3 + Quasar + TypeScript)

Структура по фичам (FSD/feature-based): `features/booking`, `entities/doctor`, `shared/api`.

```ts
// features/booking/useBookAppointment.ts
export function useBookAppointment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (slotId: number) =>
      api.POST('/appointments', { body: { slotId }, params: { header: { 'Idempotency-Key': crypto.randomUUID() } } }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['slots'] }); qc.invalidateQueries({ queryKey: ['my-appointments'] }) },
    onError: (e) => { if (isConflict(e)) notify('Слот уже занят, выберите другой'); else notify('Не удалось записаться') },
  })
}
```

```vue
<script setup lang="ts">
const { data: slots, isLoading, isError } = useSlots(doctorId, weekStart)
const book = useBookAppointment()
</script>
<template>
  <q-skeleton v-if="isLoading" />
  <q-banner v-else-if="isError" class="bg-negative text-white">Не удалось загрузить расписание <q-btn flat label="Повторить" @click="refetch()" /></q-banner>
  <q-list v-else>
    <q-item v-for="s in slots" :key="s.id" clickable :disable="book.isPending.value" @click="book.mutate(s.id)">
      <q-item-section>{{ formatTime(s.startsAt) }}</q-item-section>
    </q-item>
  </q-list>
</template>
```

Важные моменты:

- **аутентификация**: `oidc-client-ts`/`keycloak-js`, Authorization Code + PKCE, токен в памяти, refresh по silent renew; axios/fetch interceptor добавляет `Authorization`, обработка 401 → релогин;
- **состояние**: серверные данные — TanStack Query (кэш, инвалидация, ретраи), UI-состояние — локальное/Pinia, фильтры — в URL;
- **UX**: состояния загрузки/ошибки/пусто, оптимистичное обновление (аккуратно), защита от двойного клика (`isPending`), понятные ошибки (из Problem Details), доступность (фокус, ARIA), адаптивность, i18n;
- **производительность**: lazy routes, code splitting, виртуализация длинных списков, кэширование запросов;
- **безопасность**: нет `v-html` с пользовательскими данными, CSP, токены не в localStorage;
- **типобезопасность**: сгенерированный клиент из OpenAPI.

## Тестирование (пирамида)

| Уровень | Что | Инструменты |
|---|---|---|
| Unit (backend) | правила домена, валидаторы | xUnit, FluentAssertions |
| **Интеграционные** (backend) | API + реальная БД в Testcontainers: бронирование, **гонки** (параллельные запросы на один слот → ровно одна успешная) | `WebApplicationFactory`, Testcontainers (PostgreSQL) |
| Контрактные | соответствие OpenAPI | Schemathesis |
| Unit/компонентные (frontend) | composables, компоненты | Vitest, Vue Test Utils/Testing Library, MSW |
| **E2E** | вход → выбор слота → запись → проверка | Playwright (с Keycloak в compose) |
| Нагрузочные | конкуренция за слоты, p95 | k6 |

Тест конкурентности:

```csharp
[Fact]
public async Task Параллельное_бронирование_одного_слота_успешно_только_у_одного()
{
    var slotId = await SeedSlot();
    var results = await Task.WhenAll(Enumerable.Range(0, 20).Select(i => Client(user: $"u{i}").PostAsync("/api/v1/appointments", Body(slotId), IdemKey())));
    results.Count(r => r.StatusCode == HttpStatusCode.Created).Should().Be(1);
    results.Count(r => r.StatusCode == HttpStatusCode.Conflict).Should().Be(19);
}
```

## Что делаем

- [ ] Схема БД с ограничениями и индексами, миграции;
- [ ] Эндпоинты каталога и записи по OpenAPI, авторизация JWT/Keycloak, валидация, Problem Details;
- [ ] Бронирование слота без двойной записи, идемпотентность, outbox + worker;
- [ ] SPA: вход (PKCE), каталог, расписание, запись, «Мои записи», отмена;
- [ ] Обработка ошибок и состояний загрузки, доступность, i18n;
- [ ] Тесты: unit, интеграционные (Testcontainers + тест гонки), компонентные, e2e;
- [ ] Кэш каталога (Redis), health checks, OpenTelemetry-инструментация;
- [ ] Документация запуска (`make up`, seed-данные).

## Результат / артефакты

- работающий сквозной сценарий в `compose` (dev): SPA, API, PostgreSQL, Redis, Keycloak;
- код backend/frontend/worker, миграции, seed, тесты и отчёт покрытия;
- e2e-тест критического пути; тест конкурентного бронирования;
- README с запуском и схемой потока данных.

## Что рассказать на собесе

- как гарантируется отсутствие двойной записи (условное обновление + уникальный индекс, транзакция, тест гонок);
- зачем outbox и идемпотентность, что происходит при повторных запросах и сбоях;
- как устроена авторизация (PKCE, валидация JWT, проверка владельца данных);
- как выбирали состояние на фронтенде и обрабатывали ошибки/конфликты в UX;
- какие тесты написаны и что ловят; что оптимизировали (индексы, кэш, проекции).
