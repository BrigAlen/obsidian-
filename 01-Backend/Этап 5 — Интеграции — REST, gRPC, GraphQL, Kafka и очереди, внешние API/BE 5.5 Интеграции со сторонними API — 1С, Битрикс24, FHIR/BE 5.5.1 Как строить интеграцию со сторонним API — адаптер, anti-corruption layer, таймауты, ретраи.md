---
type: topic
domain: backend
stage: 5
section: "5.5"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981e6845fee5306c0eb22
tags: [domain/backend, stage/5, level/middle, topic/integration, topic/resilience, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Как строить интеграцию со сторонним API: адаптер, anti-corruption layer, таймауты, ретраи

↑ [[BE 5.5 Интеграции со сторонними API — 1С, Битрикс24, FHIR|5.5 Интеграции со сторонними API: 1С, Битрикс24, FHIR]] · → [[BE 5.5.2 HTTP-клиенты — HttpClientFactory, typed clients, Refit, RestSharp|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

























> [!info] Зачем это на собесе
> Про надёжность: что вы делаете, когда внешний сервис медленный, падает или меняет формат.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Внешняя система не под вашим контролем: у неё свои модели, лимиты и простои. Поэтому интеграцию изолируют.

| Приём | Зачем |
|---|---|
| Адаптер (порт + реализация) | доменный код зависит от своего интерфейса `IPaymentGateway`, а не от SDK |
| Anti-corruption layer (ACL) | перевод чужой модели в свою; чужие термины не протекают в домен |
| Таймауты | ограничить ожидание (на попытку и общий) |
| Retry с backoff + jitter | пережить кратковременные сбои; только идемпотентные вызовы |
| Circuit breaker | не долбить упавший сервис, быстро отказывать |
| Bulkhead / лимит параллелизма | сбой интеграции не забирает все потоки/соединения |
| Кэш и деградация | отдать последнее известное значение |
| Идемпотентность | ключи/дедупликация при повторах |
| Наблюдаемость | метрики, трейсы, логи запросов к внешним API (без секретов) |

```csharp
public interface IPaymentGateway { Task<PaymentResult> ChargeAsync(Charge c, CancellationToken ct); }

public class AcmePaymentGateway(HttpClient http) : IPaymentGateway
{
    public async Task<PaymentResult> ChargeAsync(Charge c, CancellationToken ct)
    {
        var resp = await http.PostAsJsonAsync("v2/charges", new AcmeChargeRequest(c.Amount.ToMinor(), c.Currency), ct);
        var dto = await resp.Content.ReadFromJsonAsync<AcmeChargeResponse>(ct);
        return AcmeMapper.ToDomain(dto!);       // ACL: чужие статусы → наши
    }
}

services.AddHttpClient<IPaymentGateway, AcmePaymentGateway>(c => c.BaseAddress = new("https://api.acme.example/"))
        .AddStandardResilienceHandler();
```

## Нюансы и подводные камни

- Ретраить платёж без ключа идемпотентности — риск двойного списания.
- Без таймаута один медленный вызов занимает поток/соединение.
- Контракт внешнего API меняется: контрактные тесты и толерантный парсинг.
- Храните «сырой» ответ для отладки (осторожно с персональными данными).
- Ограничения провайдера (rate limit) учитывайте на своей стороне.

## Практика

1. Оберните сторонний SDK адаптером и напишите тесты с fake.
2. Настройте таймауты, retry и circuit breaker и сымитируйте отказ через WireMock.
3. Добавьте метрики успешных/неуспешных вызовов.

## Вопросы с ответами

> [!question]- Что такое anti-corruption layer?
> Слой перевода между чужой и своей моделью, не позволяющий внешним понятиям проникать в домен.

> [!question]- Когда можно ретраить?
> Для идемпотентных операций и временных ошибок (5xx, таймаут, 429); для неидемпотентных — с ключом идемпотентности.

> [!question]- Зачем circuit breaker?
> Быстрый отказ при заведомо неработающем сервисе экономит ресурсы и даёт ему восстановиться.

## Связанные темы

- [[N:3ea33104867981289a30fe09384fdd52]]
- [[N:3ea331048679818db18de06d285c2054]]
