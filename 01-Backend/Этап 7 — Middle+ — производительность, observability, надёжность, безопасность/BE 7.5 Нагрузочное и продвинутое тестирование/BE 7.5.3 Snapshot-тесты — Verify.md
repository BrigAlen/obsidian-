---
type: topic
domain: backend
stage: 7
section: "7.5"
order: 3
status: todo
level: senior
notion_id: 3ea331048679814d9f71d46fb7e29db2
tags: [domain/backend, stage/7, level/senior, topic/testing, topic/snapshot, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Snapshot-тесты: Verify

↑ [[BE 7.5 Нагрузочное и продвинутое тестирование|7.5 Нагрузочное и продвинутое тестирование]] · ← [[BE 7.5.2 Архитектурные тесты — NetArchTest, ArchUnitNET|Предыдущая]] · → [[BE 7.5.4 Мутационное тестирование — Stryker.NET|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Когда удобнее сравнивать результат с эталоном, а не писать сотни Assert.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Snapshot-тест сохраняет результат (JSON, текст, HTML, PDF-текст) в файл-эталон и при следующих запусках сравнивает с ним. Библиотека **Verify** для .NET.

```csharp
[Fact]
public Task Order_response_matches_snapshot() =>
    Verify(new { order.Number, order.Status, Items = order.Items.Select(i => new { i.Sku, i.Qty }) });
// хранит OrdersTests.Order_response_matches_snapshot.verified.txt рядом с тестом

[Fact]
public async Task Api_returns_expected_body()
{
    var resp = await client.GetAsync("/orders/42");
    await Verify(resp).UseDirectory("snapshots");   // статус, заголовки, тело
}
```

При различии создаётся `.received.txt`; разработчик проверяет diff и принимает (`verify` tool) как новый эталон.

Применение: ответы API, сгенерированный SQL, документы и отчёты, сериализация контрактов, результат маппинга, сообщения об ошибках.

Нестабильные значения (Guid, даты) обрабатываются встроенным скраббингом: `Guid_1`, `DateTime_1` или `.ScrubMember("CreatedAt")`.

## Нюансы и подводные камни

- Эталоны нужно ревьюить: бездумное «принять всё» превращает тест в шум.
- Слишком большие снимки сложно читать; ограничивайте содержимое значимым.
- Изменение формата сериализации ломает много снимков: используйте стабильные DTO.
- Не храните секреты в эталонах.

## Практика

1. Добавьте Verify для ответа одного API и для сгенерированного отчёта.
2. Настройте скраббинг Guid и дат.
3. Включите `.verified.*` в git и `.received.*` в `.gitignore`.

## Вопросы с ответами

> [!question]- Когда snapshot-тест лучше Assert?
> Когда результат большой и структурированный, и сравнение с эталоном понятнее набора отдельных проверок.

> [!question]- Основной риск snapshot-тестов?
> Автоматическое принятие изменений без ревью.

## Связанные темы

- [[N:3ea3310486798178b3e8f59001897e71]]
- [[N:3ea331048679818fb3f5e72ce72ba06c]]
