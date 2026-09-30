---
type: topic
domain: devops
stage: 7
order: 4
status: todo
level: middle+
tags: [domain/devops, stage/7, level/middle+, priority/should]
reviewed: 
next_review: 
priority: should
time: 7
---

# Логи: ELK, Loki, централизованный сбор

↑ [[DO Этап 7 · Observability и эксплуатация|Этап 7 · Observability и эксплуатация]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Централизованные логи — основа расследований. Спрашивают сравнение ELK и Loki, структурированные логи и конвейер сбора.

## Зачем централизовать

Логи на серверах и в контейнерах исчезают при пересоздании, разбросаны по узлам, недоступны разработчикам. Централизованная система даёт: поиск по всем сервисам, корреляцию по `trace_id`, хранение и ретенцию, алерты по логам, аудит.

## Структурированные логи

Предпочитайте **JSON** с постоянными полями:

```json
{"ts":"2026-09-30T12:00:01.123Z","level":"error","service":"api","env":"prod","trace_id":"4bf92f3577b34da6a3ce929d0e0e4736","span_id":"00f067aa0ba902b7","user_id":"u-42","msg":"Payment failed","error":"timeout","duration_ms":3012}
```

Правила: уровни (`debug/info/warn/error/fatal`), единое время (UTC, ISO 8601), корреляционные идентификаторы, **без секретов и ПДн** (маскирование), сообщения — фиксированный текст + поля (а не интерполяция в строку), контролируемый объём (debug выключен в проде), логи в **stdout/stderr** в контейнерах. .NET: Serilog/Microsoft.Extensions.Logging + OpenTelemetry (`AddOpenTelemetry` logging), `Serilog.Sinks.Console` JSON (CompactJsonFormatter).

## Конвейер сбора

```text
Приложение (stdout / файлы) → Агент на узле (Fluent Bit, Vector, Promtail, OTel Collector, Filebeat)
    → [буфер/очередь: Kafka] → Хранилище (Loki | Elasticsearch/OpenSearch | ClickHouse) → UI (Grafana | Kibana)
```

Агент: читает файлы логов контейнеров (`/var/log/containers`, journald), **парсит**, **обогащает** метаданными (namespace, pod, labels, node), **фильтрует/маскирует**, батчит, повторяет при ошибках, держит backpressure/диск-буфер. Варианты: DaemonSet (один агент на ноду), sidecar (особые случаи), прямая отправка из приложения (OTLP; зависимость от сети).

## ELK / EFK

**Elasticsearch** (поиск и хранилище, инвертированный индекс) + **Logstash** (обработка, тяжёлый) или **Beats/Fluentd/Fluent Bit** + **Kibana** (UI).

- полнотекстовый поиск по любому полю, агрегации, мощная аналитика, ML;
- **индексы** по времени (`logs-2026.09.30`), **ILM** (hot → warm → cold → delete), шаблоны и маппинги (типы полей!), шарды/реплики;
- плюсы: богатый поиск, зрелая экосистема, визуализация, SIEM-возможности;
- минусы: **ресурсоёмкий** (RAM/диск: индексируется всё), сложность эксплуатации (кластер, шарды, маппинги, reindex), лицензия (SSPL/Elastic License; форк **OpenSearch**), стоимость хранения.

## Grafana Loki

«Prometheus для логов»: **индексирует только метки** (namespace, app, pod), а **содержимое хранится сжатыми чанками** (объектное хранилище S3/MinIO); поиск по тексту — фильтрацией при запросе (LogQL).

```text
{namespace="clinic", app="api"} |= "timeout" != "healthcheck"            # фильтры строк
{app="api"} | json | level="error" | duration_ms > 1000                   # парсинг и фильтр по полям
sum by (app) (rate({namespace="clinic"} | json | level="error" [5m]))     # метрики из логов
topk(5, sum by (route) (count_over_time({app="api"} | json [1h])))
```

- плюсы: **дёшево и просто** (малый индекс, объектное хранилище), интеграция с Grafana/Prometheus (те же метки), быстрый старт;
- минусы: медленный полнотекстовый поиск по большим объёмам без меток, ограничения по высокой кардинальности меток, аналитика слабее Elasticsearch;
- агенты: **Promtail** (legacy), **Grafana Alloy**, Fluent Bit, Vector, OTel Collector;
- режимы: монолит, simple scalable, микросервисный; хранилище: S3/GCS/MinIO, retention и compactor;
- **метки**: только низкая кардинальность (namespace, app, env, level); `pod`/`trace_id`/`user_id` — в содержимое логов.

## ClickHouse для логов

Колоночное хранилище с SQL: очень высокое сжатие, быстрые агрегации, хорошо для логов/трейсов OTel (схемы `otel_logs`, `otel_traces`), SigNoz, HyperDX, ClickStack, Uptrace; + долговременное хранение и аналитика, TTL. Минусы: нужен UI/запросы SQL, собственная схема и эксплуатация.

## Сравнение

| | Elasticsearch/OpenSearch | Loki | ClickHouse |
|---|---|---|---|
| Индексация | всё (инвертированный) | только метки | разреженный индекс + колонки |
| Полнотекстовый поиск | очень быстрый | через grep-подобную фильтрацию | через токен-индексы, `hasToken`, `LIKE` |
| Стоимость хранения | высокая | низкая | низкая |
| Аналитика/агрегации | хорошая | ограничена | отличная (SQL) |
| Эксплуатация | сложная | проще | средняя |
| Интеграция с Grafana | есть | нативная | плагин |
| Подходит | поиск и SIEM, сложные запросы | K8s, DevOps-логи, бюджет | большие объёмы, аналитика, единый стек OTel |

## Парсинг и обработка

- **grok/regex** для нестандартных форматов (nginx access, syslog) — лучше перевести источники на JSON;
- multiline (stack trace): `multiline` парсеры (Fluent Bit `multiline.parser`), склейка по началу записи;
- обогащение: `k8sattributes`, геолокация по IP, теги среды;
- **маскирование ПДн/секретов** на агенте (регулярки, `redact`);
- **семплирование/фильтрация шума** (health checks, debug), ограничение скорости (rate limit) на сервис;
- единые **поля** (ECS — Elastic Common Schema / OTel semantic conventions): `service.name`, `trace_id`, `http.status_code`.

```ini
# Fluent Bit (фрагмент)
[INPUT]
    Name tail
    Path /var/log/containers/*.log
    multiline.parser docker, cri
    Tag kube.*
[FILTER]
    Name kubernetes
    Match kube.*
    Merge_Log On
[FILTER]
    Name modify
    Match kube.*
    Remove password
[OUTPUT]
    Name loki
    Match kube.*
    Host loki
    Labels namespace=$kubernetes['namespace_name'], app=$kubernetes['labels']['app'], level=$level
```

## Ретенция, стоимость, безопасность

- хранение: горячее (7–14 дней), тёплое/холодное (30–90 дней), архив (S3, год+ по требованиям); удаление ПДн по запросу;
- контроль объёма: уровни, sampling, исключение шума, метрики вместо логов для счётчиков;
- доступ: RBAC по командам/namespace, мультиарендность (`X-Scope-OrgID` в Loki), аудит запросов; шифрование в пути и на диске;
- целостность и неизменяемость для аудита (WORM-хранилище);
- соответствие: PCI DSS, GDPR, 152-ФЗ;
- мониторинг самой системы логов: потеря сообщений, лаг, ошибки парсинга, заполнение дисков, скорость приёма.

## Практики эксплуатации

- **логи → метрики → алерты** (LogQL `rate`, `count_over_time`, Elasticsearch watcher/ES|QL alert);
- **корреляция**: `trace_id` во всех логах; переход лог ↔ трейс;
- **один формат** и библиотека логирования на всех сервисах;
- не терять логи при пиках: буферы агента, Kafka, backpressure; политика при переполнении;
- тест: «найдите за 5 минут причину ошибки пользователя по `request_id`».

## Вопросы с ответами

> [!question]- Чем Loki отличается от Elasticsearch?
> Loki индексирует только метки, а содержимое хранит сжатыми чанками и фильтрует при запросе — дёшево и просто, но слабее по полнотекстовому поиску и аналитике. Elasticsearch индексирует всё: быстрый поиск и богатые агрегации, но дороже и сложнее.

> [!question]- Почему метки в Loki должны иметь низкую кардинальность?
> Каждая уникальная комбинация меток создаёт отдельный поток и увеличивает индекс; высококардинальные значения (user_id, trace_id) нужно хранить в содержимом лога.

> [!question]- Зачем структурированные логи?
> Поля можно надёжно фильтровать и агрегировать без хрупкого разбора текста, коррелировать с трейсами и строить метрики и алерты.
