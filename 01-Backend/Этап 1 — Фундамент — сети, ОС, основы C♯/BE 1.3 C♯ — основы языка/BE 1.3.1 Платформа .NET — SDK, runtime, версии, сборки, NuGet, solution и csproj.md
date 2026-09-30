---
type: topic
domain: backend
stage: 1
section: "1.3"
order: 1
status: todo
level: junior
notion_id: 3ea3310486798179857cd5196aee4d71
tags: [domain/backend, stage/1, level/junior, topic/dotnet, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Платформа .NET: SDK, runtime, версии, сборки, NuGet, solution и csproj

↑ [[BE 1.3 C♯ — основы языка|1.3 C♯: основы языка]] · → [[BE 1.3.2 Типы — value и reference, struct и class, CTS|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->





































> [!info] Зачем это на собесе
> базовые вопросы любого .NET-собеса: что такое .NET, чем SDK отличается от runtime, что такое сборка, как устроен solution. В проекте 80+ проектов в одном solution (`corebackend.slnx`), так что это ещё и практика.

## Объяснение

### Что такое .NET сегодня

- **.NET** (бывший .NET Core) — кроссплатформенная open-source платформа: Windows, Linux, macOS, контейнеры. Версии: .NET 8 (LTS, поддержка 3 года), .NET 9 (STS, 18 месяцев), .NET 10 (LTS).
- **.NET Framework 4.x** — старая платформа только для Windows, в режиме поддержки.
- **.NET Standard** — устаревшая спецификация общего API для библиотек, совместимых со старым Framework (в проекте один `netstandard2.0` — генератор исходников Roslyn, которому это требуется).

### SDK и runtime

- **Runtime** (`Microsoft.NETCore.App`, `Microsoft.AspNetCore.App`) — нужен для **запуска**: CLR, базовые библиотеки.
- **SDK** — для **разработки и сборки**: компилятор Roslyn, MSBuild, CLI `dotnet`, шаблоны. Включает runtime.
- В Docker: сборка в образе `mcr.microsoft.com/dotnet/sdk:9.0`, запуск в `aspnet:9.0` (multi-stage), чтобы финальный образ был меньше.
- `global.json` фиксирует версию SDK для репозитория.

### Сборка (assembly)

- Результат компиляции проекта: `.dll` (или `.exe`) с **IL-кодом** и **метаданными** (типы, члены, ссылки).
- Единица развёртывания, версионирования и безопасности. Модификатор `internal` = видно только внутри сборки (или для `InternalsVisibleTo`, например тестам).
- При запуске CLR загружает сборки и JIT-компилирует IL в машинный код.

### Проект и solution

- **`.csproj`** — SDK-style MSBuild-файл: целевой фреймворк, зависимости, настройки.
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Npgsql.EntityFrameworkCore.PostgreSQL" Version="9.0.4" />
    <ProjectReference Include="..\..\core\domain\domain.csproj" />
  </ItemGroup>
</Project>
```
- **Solution** (`.sln` или новый XML-формат `.slnx`) — набор проектов для IDE и сборки.
- **Directory.Build.props** — общие настройки для всех проектов в каталоге и ниже (версия языка, анализаторы, nullable).
- **Directory.Packages.props** — централизованное управление версиями NuGet (Central Package Management): одна версия пакета на весь solution.

### NuGet

Пакетный менеджер .NET. `dotnet add package`, `dotnet restore`. Свои пакеты (общее ядро микросервисов) публикуют во внутренний feed (GitLab Package Registry).

### CLI

```bash
dotnet new webapi -n PatientApi
dotnet build -c Release
dotnet test
dotnet run --project src/PatientApi
dotnet publish -c Release -o out     # подготовка к деплою
dotnet ef migrations add Init        # инструменты (dotnet-tools.json)
```

### Варианты публикации

- **Framework-dependent** — нужен установленный runtime (обычный вариант в Docker-образе aspnet).
- **Self-contained** — runtime включён в вывод, больше размер.
- **Single-file**, **trimming** (удаление неиспользуемого кода), **Native AOT** (компиляция в нативный бинарник: быстрый старт, мало памяти, но ограничения на рефлексию).

## Нюансы и подводные камни

- Разные версии одного пакета в разных проектах solution → конфликты при сборке (NU1605, MSB3277). Лечится Central Package Management.
- `TreatWarningsAsErrors` + `Nullable` в общем `Directory.Build.props` — дешёвый способ поднять качество кода во всех сервисах.
- Смешение net8.0 и net9.0 в одном solution допустимо, но общие библиотеки должны быть совместимы по TFM.
- `bin/` и `obj/` не коммитить, `packages.lock.json` — по желанию, для воспроизводимых сборок.

## Вопросы с ответами

> [!question]- Чем .NET отличается от .NET Framework?
> .NET (бывший Core) кроссплатформенный, open source, быстрее, с новыми версиями каждый год. .NET Framework работает только на Windows, находится на поддержке, новых фич нет.

> [!question]- Чем SDK отличается от runtime?
> Runtime нужен для запуска приложения (CLR и библиотеки). SDK — для разработки: компилятор, MSBuild, CLI, шаблоны. SDK включает runtime.

> [!question]- Что такое сборка и что в ней хранится?
> Результат компиляции проекта (dll или exe): IL-код, метаданные типов, манифест с версией и зависимостями. Единица развёртывания и границы видимости internal.

> [!question]- Как управлять общими настройками и версиями пакетов в большом solution?
> Directory.Build.props для общих свойств (LangVersion, Nullable, анализаторы) и Directory.Packages.props (Central Package Management) для единых версий NuGet.

> [!question]- Что такое LTS и почему это важно?
> Long Term Support: чётные версии .NET (8, 10) поддерживаются 3 года. Для продакшена чаще выбирают LTS, чтобы реже мигрировать.

## Связанные темы

- Следующая: [[N:3ea33104867981948314ef0273ece7b5]]
- CLR, JIT, AOT: [[N:3ea331048679811dbdcde35749fbe9b4]]
- Multi-stage build для .NET: [[N:3ea3310486798182a842d9f1a8be6b0e]]
- Общий код между сервисами (NuGet): [[N:3ea3310486798108a3caf17276ee36aa]]
- Что нового в C# и .NET: [[N:3ea331048679811a82c2d9502acd1026]]
