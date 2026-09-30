---
type: topic
domain: backend
stage: 1
section: "1.2"
order: 5
status: todo
level: junior
notion_id: 3ea3310486798180a101f27fb02bd5ef
tags: [domain/backend, stage/1, topic/os, topic/datetime, topic/encoding, level/junior, flag/rewritten, priority/should]
rewritten: true
reviewed:
next_review:
priority: should
time: 6
---

# Кодировки, часовые пояса, время на сервере

↑ [[BE 1.2 ОС и Linux для разработчика|1.2 ОС и Linux для разработчика]] · ← [[BE 1.2.4 Linux и shell для бэкендера — логи, сигналы, переменные окружения|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->










> [!note] Переписано
> В Notion эта страница содержала шаблонный текст без отношения к теме. Здесь — содержательная версия.

> [!info] Зачем это на собесе
> Баги со временем и кодировками — самые «дорогие» и незаметные: «кракозябры» в PDF и CSV, записи, «уехавшие» на час после перехода на летнее время, разные результаты на сервере и у клиента. Вопрос «как хранить и передавать время?» задают почти всегда.

## Подтемы
- [ ] Unicode и UTF-8, BOM, кодировки в .NET
- [ ] Время: UTC, часовые пояса, DST
- [ ] DateTime, DateTimeOffset, DateOnly, TimeProvider
- [ ] Хранение времени в PostgreSQL
- [ ] Часы на сервере: NTP, дрейф, монотонное время

## Объяснение

### Кодировки
- **Unicode** — таблица символов (code points). **UTF-8** — кодировка переменной длины (1–4 байта), совместима с ASCII; стандарт для веба, JSON и Linux.
- UTF-16 — внутреннее представление `string` в .NET (символ = 1–2 `char`, суррогатные пары для эмодзи).
- **BOM** (`EF BB BF`) — метка порядка байтов в начале файла; нужна некоторым программам (Excel для CSV в UTF-8), но ломает парсеры JSON и shell-скрипты.
- Причина «кракозябр» — данные закодированы одной кодировкой, а прочитаны другой (UTF-8 vs Windows-1251).
```csharp
var bytes = Encoding.UTF8.GetBytes("Привет");          // кодирование
var text  = Encoding.UTF8.GetString(bytes);            // декодирование

// CSV для Excel: UTF-8 с BOM
await File.WriteAllTextAsync("report.csv", csv, new UTF8Encoding(encoderShouldEmitUTF8Identifier: true));

// Длина «видимых» символов, а не char
var info = new System.Globalization.StringInfo("e\u0301");
Console.WriteLine(info.LengthInTextElements);          // 1
```
- В HTTP кодировку задаёт `Content-Type: application/json; charset=utf-8`. `System.Text.Json` работает с UTF-8.
- В PostgreSQL кодировку базы задают при создании (`UTF8`); collation влияет на сортировку и сравнение строк.

### Время: главное правило
> **Хранить и передавать в UTC, переводить в локальное время только на границе показа пользователю.**

- **UTC** — универсальная шкала без переходов. **Часовой пояс** — правило смещения (IANA: `Europe/Moscow`, `America/New_York`), у которого бывают переходы на летнее время (DST) и исторические изменения.
- Смещение (`+03:00`) ≠ часовой пояс: смещение — число на конкретный момент, пояс — набор правил.
- Формат обмена: ISO 8601 (`2026-09-30T12:31:14Z` или с `+03:00`).

### Типы времени в .NET
| Тип | Что хранит | Когда использовать |
|---|---|---|
| `DateTime` | тики + `Kind` (Utc/Local/Unspecified) | осторожно: `Kind` легко потерять |
| `DateTimeOffset` | момент времени + смещение | момент события (создан, оплачен) |
| `DateOnly` / `TimeOnly` | дата / время суток без пояса | день рождения, расписание |
| `TimeSpan` | длительность | интервалы, таймауты |
| `TimeZoneInfo` | правила пояса | конвертация в локальное время пользователя |
```csharp
var utc = DateTimeOffset.UtcNow;
var tz  = TimeZoneInfo.FindSystemTimeZoneById("Europe/Moscow");   // IANA id работает на Linux и Windows (.NET 6+)
var local = TimeZoneInfo.ConvertTime(utc, tz);

// Тестируемое время: TimeProvider (встроен с .NET 8)
public class TokenService(TimeProvider clock)
{
    public bool IsExpired(DateTimeOffset expiresAt) => clock.GetUtcNow() >= expiresAt;
}
// в тесте: var fake = new FakeTimeProvider(); fake.Advance(TimeSpan.FromMinutes(5));
```

### Время в PostgreSQL
- `timestamptz` — момент времени; внутри хранится в UTC, при выводе конвертируется в пояс сессии. **Использовать по умолчанию.**
- `timestamp` (без tz) — «настенное» время без пояса, подходит для будущих запланированных событий в локальном времени.
- Npgsql 6+: `DateTime` с `Kind=Utc` ↔ `timestamptz`; попытка записать `Kind=Local` или `Unspecified` в `timestamptz` — исключение. Это защита, не баг.

### Часы сервера
- Часы серверов расходятся (дрейф) — синхронизация по **NTP** (`chrony`, `systemd-timesyncd`). Расхождение ломает JWT (`nbf`/`exp`), TOTP, подписи запросов, порядок событий в логах.
- Для измерения длительности используйте **монотонные часы** (`Stopwatch`, `Environment.TickCount64`), а не разность `DateTime.UtcNow`: системное время может скакнуть назад.
- Контейнер использует часы хоста; часовой пояс контейнера по умолчанию UTC (`TZ` переменная и `tzdata` в образе для локального пояса; в chiseled/alpine-образах `tzdata` может отсутствовать → `TimeZoneNotFoundException`).

## Нюансы и подводные камни
- `DateTime.Now` на сервере даёт пояс сервера — результат зависит от окружения. В серверном коде используйте `UtcNow` или `TimeProvider`.
- Переход на летнее время: локальные времена бывают несуществующими (пропущенный час) и неоднозначными (повторяющийся час) — `TimeZoneInfo.IsInvalidTime` / `IsAmbiguousTime`.
- «Каждый день в 03:00» — cron в UTC даст сдвиг для пользователей с DST; задача, зависящая от локального времени, планируется с учётом пояса.
- Сравнение дат без времени: `date.Date` и границы суток в UTC ≠ границы суток пользователя.
- JSON: `DateTime` без `Z` десериализуется с `Kind=Unspecified`; убедитесь, что клиенты шлют `Z` или смещение.
- Не сортируйте и не сравнивайте даты как строки в нестандартных форматах.

## Вопросы с ответами
> [!question]- Как хранить и передавать время в API и БД?
> В UTC, в формате ISO 8601 с `Z` или смещением; в PostgreSQL — `timestamptz`; в .NET — `DateTimeOffset`/`DateTime` с `Kind=Utc`. Конвертация в локальный пояс — на клиенте или на границе показа.

> [!question]- Чем DateTime отличается от DateTimeOffset?
> `DateTime` хранит тики и `Kind`, но не смещение: `Local`/`Unspecified` неоднозначны. `DateTimeOffset` хранит момент и смещение, однозначно определяя точку на шкале времени.

> [!question]- Чем UTF-8 отличается от UTF-16 и что такое BOM?
> UTF-8 — 1–4 байта на символ, совместим с ASCII, стандарт для сети. UTF-16 — 2 или 4 байта, внутреннее представление `string` в .NET. BOM — метка в начале файла, указывающая кодировку/порядок байтов; для UTF-8 не обязательна и может мешать парсерам.

> [!question]- Как протестировать код, зависящий от текущего времени?
> Не обращаться к `DateTime.UtcNow` напрямую, а внедрять `TimeProvider` (или `IClock`) и подменять его в тестах на `FakeTimeProvider`.

> [!question]- Почему после DST «задача сработала дважды/не сработала»?
> Локальное время в момент перевода часов бывает неоднозначным или несуществующим. Планируйте в UTC или явно обрабатывайте эти случаи с `TimeZoneInfo`.

> [!question]- Почему нельзя измерять длительность через DateTime.UtcNow?
> Системные часы могут корректироваться (NTP, ручная правка), время «прыгнет». Для измерений — монотонный `Stopwatch`.

## Связанные темы
- Предыдущая: [[N:3ea331048679818c8019d4ec5550c756]]
- Value-типы и структуры: [[N:3ea33104867981948314ef0273ece7b5]]
- Типы данных PostgreSQL: [[N:3ea331048679810296f9f0746b766fdb]]
- JWT и время жизни токенов: [[N:3ea331048679813eb08fc62e6abf2bb5]]
