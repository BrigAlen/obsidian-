---
type: topic
domain: backend
stage: 7
section: "7.5"
order: 2
status: todo
level: senior
notion_id: 3ea3310486798178b3e8f59001897e71
tags: [domain/backend, stage/7, level/senior, topic/testing, topic/architecture, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Архитектурные тесты: NetArchTest, ArchUnitNET

↑ [[BE 7.5 Нагрузочное и продвинутое тестирование|7.5 Нагрузочное и продвинутое тестирование]] · ← [[BE 7.5.1 Нагрузочное тестирование — k6, NBomber, метрики и профили нагрузки|Предыдущая]] · → [[BE 7.5.3 Snapshot-тесты — Verify|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



































> [!info] Зачем это на собесе
> Как автоматически удерживать архитектурные правила в большой команде.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Архитектурные тесты проверяют структуру кода: зависимости между слоями, имена, наследование, доступность.

```csharp
public class ArchitectureTests
{
    private static readonly Assembly Domain = typeof(Order).Assembly;
    private static readonly Assembly Infrastructure = typeof(AppDbContext).Assembly;

    [Fact]
    public void Domain_should_not_depend_on_infrastructure()
    {
        var result = Types.InAssembly(Domain).ShouldNot().HaveDependencyOn("Orders.Infrastructure").GetResult();
        Assert.True(result.IsSuccessful, string.Join(", ", result.FailingTypeNames ?? []));
    }

    [Fact]
    public void Handlers_should_be_sealed_and_named_Handler()
    {
        var result = Types.InAssembly(typeof(Program).Assembly).That().ImplementInterface(typeof(IRequestHandler<,>))
            .Should().BeSealed().And().HaveNameEndingWith("Handler").GetResult();
        Assert.True(result.IsSuccessful);
    }
}
```

Что типично проверять:

- Направление зависимостей (Clean Architecture: Domain не зависит ни от чего).
- Отсутствие циклических зависимостей между модулями монолита.
- Контроллеры не обращаются к репозиториям напрямую.
- Соглашения именования и модификаторы (`internal` по умолчанию).
- Запрет использования устаревших API.

Библиотеки: NetArchTest.Rules, ArchUnitNET; в модульных монолитах — проверка границ модулей.

## Нюансы и подводные камни

- Слишком детальные правила замедляют команду и вызывают «обход» правил.
- Тесты дополняют, но не заменяют ревью.
- Анализаторы Roslyn (`Microsoft.CodeAnalysis`) проверяют правила на этапе компиляции.
- Правила должны быть согласованы командой и задокументированы (ADR).

## Практика

1. Добавьте тест «Domain не зависит от Infrastructure».
2. Запретите циклические зависимости между модулями.
3. Реализуйте правило, что публичные типы модуля находятся только в контракте.

## Вопросы с ответами

> [!question]- Зачем архитектурные тесты?
> Автоматически предотвращают нарушение договорённостей о структуре кода, которые иначе размываются со временем.

> [!question]- Чем архитектурные тесты отличаются от анализаторов?
> Тесты запускаются в CI и проверяют скомпилированные сборки; анализаторы работают в компиляторе и IDE.

## Связанные темы

- [[N:3ea3310486798123bb38cfb5a6dba784]]
- [[N:3ea331048679814d9f71d46fb7e29db2]]
