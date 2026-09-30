---
type: section
domain: backend
stage: 2
section: "2.3"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981a9bca1efaa4f336770
tags: [domain/backend, stage/2, kind/section]
---

# 2.3 Асинхронность и многопоточность

↑ [[BE Этап 2 · C♯ глубоко и .NET runtime|Этап 2]]

Потоки, Task, async/await, синхронизация, каналы и типичные ошибки.

## Темы
<!-- toc:start -->
**Итого:** 10 тем · ~51 мин · готово 0 из 10

<div class="bar"><span style="width:0%"></span></div>

| # | Тема | Приоритет | Чтение | Статус |
|---|---|---|---|---|
| 1 | [[BE 2.3.1 Thread и ThreadPool\|Thread и ThreadPool]] | <span class="badge must">Обязательно</span> | 5 мин | <span class="badge todo">Не начато</span> |
| 2 | [[BE 2.3.2 Task и TPL\|Task и TPL]] | <span class="badge must">Обязательно</span> | 6 мин | <span class="badge todo">Не начато</span> |
| 3 | [[BE 2.3.3 async-await изнутри — state machine, SynchronizationContext, ConfigureAwait\|async∕await изнутри: state machine, SynchronizationContext, ConfigureAwait]] | <span class="badge must">Обязательно</span> | 6 мин | <span class="badge todo">Не начато</span> |
| 4 | [[BE 2.3.4 ValueTask и аллокации\|ValueTask и аллокации]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 5 | [[BE 2.3.5 CancellationToken и таймауты\|CancellationToken и таймауты]] | <span class="badge must">Обязательно</span> | 6 мин | <span class="badge todo">Не начато</span> |
| 6 | [[BE 2.3.6 Синхронизация — lock, Monitor, SemaphoreSlim, Interlocked, ReaderWriterLockSlim\|Синхронизация: lock, Monitor, SemaphoreSlim, Interlocked, ReaderWriterLockSlim]] | <span class="badge must">Обязательно</span> | 8 мин | <span class="badge todo">Не начато</span> |
| 7 | [[BE 2.3.7 Race condition, deadlock, livelock, starvation\|Race condition, deadlock, livelock, starvation]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 8 | [[BE 2.3.8 Потокобезопасные коллекции и Channels\|Потокобезопасные коллекции и Channels]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 9 | [[BE 2.3.9 Parallel, PLINQ, Task.WhenAll и ограничение параллелизма\|Parallel, PLINQ, Task.WhenAll и ограничение параллелизма]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 10 | [[BE 2.3.10 Антипаттерны — async void, .Result, sync over async\|Антипаттерны: async void, .Result, sync over async]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
<!-- toc:end -->

## Чек-лист раздела
- [ ] Прочитал все темы
- [ ] Могу объяснить каждую тему за 2 минуты вслух
