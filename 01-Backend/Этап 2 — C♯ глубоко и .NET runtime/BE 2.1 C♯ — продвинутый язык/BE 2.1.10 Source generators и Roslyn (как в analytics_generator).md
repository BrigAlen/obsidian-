---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 10
status: todo
level: middle
notion_id: 3ea331048679816ca016dc47df98b9ec
tags: [domain/backend, stage/2, level/middle, topic/roslyn, topic/codegen, priority/must]
reviewed:
next_review:
priority: must
time: 8
---

# Source generators и Roslyn (как в analytics_generator)

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.9 Атрибуты и рефлексия|Предыдущая]] · → [[BE 2.1.11 Сериализация — System.Text.Json и Newtonsoft|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

































































> [!info] Зачем это на собесе
> source generators заменяют рефлексию генерацией кода при компиляции: быстрее, AOT-совместимо, ошибки видны сразу. В проекте есть свой генератор (`analytics_generator`), который по атрибутам профилей создаёт маппинг ресурсов в строки ClickHouse, реестр и диспетчер. Это сильная тема для рассказа на собесе.

## Объяснение

### Roslyn

Компилятор C# с открытым API: синтаксические деревья, семантическая модель (символы, типы). На нём построены анализаторы (warnings в IDE), code fixes и **source generators**.

### Source generator

Компонент, который **во время компиляции** анализирует код проекта и **добавляет новые файлы C#** в компиляцию. Существующий код менять не может, только дополнять (поэтому связка с `partial`).
Современный API — **`IIncrementalGenerator`**: конвейер с кэшированием, пересчитываются только изменившиеся части. Это важно, чтобы IDE не тормозила.

### Как устроен генератор в проекте (упрощённо)

```csharp
[Generator(LanguageNames.CSharp)]
public sealed class AnalyticsRowGenerator : IIncrementalGenerator
{
    public void Initialize(IncrementalGeneratorInitializationContext context)
    {
        // маркерный файл: доказывает, что генератор вообще загрузился
        context.RegisterPostInitializationOutput(ctx => ctx.AddSource("__Loaded.g.cs", "// loaded"));

        // найти классы с атрибутом [AnalyticsProfile(...)] — быстрый путь через ForAttributeWithMetadataName
        var profiles = context.SyntaxProvider.ForAttributeWithMetadataName(
                "analytics_models.AnalyticsProfileAttribute",
                predicate: static (node, _) => node is ClassDeclarationSyntax,
                transform: static (ctx, ct) => Build(ctx, ct))      // семантическая модель → своя модель данных
            .Where(static m => m is not null)
            .Select(static (m, _) => m!);

        // на каждый профиль — свой файл с маппингом
        context.RegisterSourceOutput(profiles, static (spc, model) =>
            spc.AddSource($"{model.TypeName}AnalyticsMap.g.cs", EmitMap(model)));

        // по всем профилям вместе — реестр и диспетчер + диагностика дубликатов ключей
        context.RegisterSourceOutput(profiles.Collect(), static (spc, all) =>
        {
            foreach (var d in FindDuplicateKeys(all)) spc.ReportDiagnostic(d);
            spc.AddSource("AnalyticsRegistry.g.cs", EmitRegistry(all));
            spc.AddSource("AnalyticsDispatcher.g.cs", EmitDispatcher(all));
        });
    }
}
```
Что это даёт: при добавлении нового профиля (класс с атрибутами `[AnalyticsColumn]`, `[AnalyticsIgnore]`, `[AnalyticsTemporal]`) маппинг в колонки ClickHouse и регистрация в диспетчере появляются **автоматически**, без рефлексии в рантайме и без ручного кода. Ошибки (дубликат ключа) видны как **ошибки компиляции**.

### Проект генератора

```xml
<PropertyGroup>
  <TargetFramework>netstandard2.0</TargetFramework>     <!-- требование: генератор грузится в компилятор -->
  <IsRoslynComponent>true</IsRoslynComponent>
  <EnforceExtendedAnalyzerRules>true</EnforceExtendedAnalyzerRules>
  <IncludeBuildOutput>false</IncludeBuildOutput>
</PropertyGroup>
<ItemGroup>
  <PackageReference Include="Microsoft.CodeAnalysis.CSharp" Version="4.8.0" PrivateAssets="all" />
</ItemGroup>

<!-- подключение в потребителе -->
<ProjectReference Include="..\analytics_generator\analytics_generator.csproj"
                  OutputItemType="Analyzer" ReferenceOutputAssembly="false" />
```
Посмотреть сгенерированный код: `<EmitCompilerGeneratedFiles>true</EmitCompilerGeneratedFiles>` → папка `obj/.../generated`.

### Встроенные генераторы в .NET

- `System.Text.Json`: `[JsonSerializable(typeof(PatientDto))] partial class AppJsonContext : JsonSerializerContext` — сериализация без рефлексии.
- `[GeneratedRegex]` — регулярка компилируется в код.
- `[LoggerMessage]` — высокопроизводительное логирование без боксинга.
- Minimal API Request Delegate Generator, Configuration Binder Generator (для AOT).
- gRPC (`Grpc.Tools`) — генерация клиентов и серверов из `.proto` (формально MSBuild-кодоген, но идея та же).
```csharp
public static partial class Log
{
    [LoggerMessage(EventId = 1001, Level = LogLevel.Information, Message = "Report {FormCode} built for {PatientId} in {Elapsed} ms")]
    public static partial void ReportBuilt(ILogger logger, string formCode, Guid patientId, long elapsed);
}
```

## Нюансы и подводные камни

- Генератор, который молча «ничего не сгенерировал», — самая неприятная ошибка. Отсюда приём с маркерным файлом в `RegisterPostInitializationOutput` и собственные `Diagnostic`.
- Модель данных конвейера должна быть **сравнимой** (records, `EquatableArray`): иначе кэш инкрементального генератора не работает, и IDE тормозит. Нельзя тащить в модель `ISymbol` и `SyntaxNode`.
- Генератор выполняется внутри компилятора: `netstandard2.0`, никаких тяжёлых зависимостей, исключение генератора = предупреждение и пустой вывод.
- Отлаживать сложно: юнит-тесты генератора через `CSharpGeneratorDriver` и снапшоты (Verify.SourceGenerators).

## Тестирование

```csharp
[Fact]
public Task Generates_map_for_profile()
{
    var source = """
        [AnalyticsProfile("encounters", "Encounter", "profile-url")]
        public partial class EncounterProfile { [AnalyticsColumn("status")] public string Status { get; set; } }
        """;
    var compilation = CSharpCompilation.Create("test", [CSharpSyntaxTree.ParseText(source)], References);
    var driver = CSharpGeneratorDriver.Create(new AnalyticsRowGenerator()).RunGenerators(compilation);
    return Verify(driver);            // snapshot сгенерированных файлов
}
```

## Вопросы с ответами

> [!question]- Что такое source generator и чем он лучше рефлексии?
> Компонент Roslyn, который при компиляции анализирует код и добавляет новые исходники. В отличие от рефлексии, работа делается на этапе сборки: нет затрат в рантайме, совместимо с trimming и AOT, ошибки видны при компиляции.

> [!question]- Чем IIncrementalGenerator лучше старого ISourceGenerator?
> Конвейер с кэшированием промежуточных результатов: пересчитываются только изменившиеся части. Это критично для производительности IDE при каждом нажатии клавиши.

> [!question]- Почему генератор должен таргетировать netstandard2.0?
> Он загружается в процесс компилятора (включая Visual Studio на .NET Framework и MSBuild), которому нужна совместимая сборка.

> [!question]- Расскажите о генераторе в своём проекте.
> Генератор находит классы-профили аналитики по атрибуту, строит модель колонок по атрибутам свойств и генерирует для каждого профиля маппинг ресурса в строку ClickHouse, а по всем профилям — реестр и диспетчер. Дубликаты ключей выдаются как ошибки компиляции. Результат: новый профиль подключается без ручного кода и без рефлексии.

## Связанные темы

- Предыдущая: [[N:3ea331048679819dabaffeca732fabc4]] · Следующая: [[N:3ea331048679818ea358eaece94428c4]]
- Атрибуты и рефлексия: [[N:3ea331048679819dabaffeca732fabc4]]
- partial: [[N:3ea331048679819c8d5af429a165212d]]
- ClickHouse: вставка данных: [[N:3ea3310486798115b9c2c7343b02da24]]
- Snapshot-тесты (Verify): [[N:3ea331048679814d9f71d46fb7e29db2]]
- Кодоген GraphQL на фронте (та же идея): [[N:3ea331048679818eacacea12f103344c]]
