---
type: topic
domain: backend
stage: 9
section: "9.2"
order: 5
status: todo
level: senior
notion_id: 3ea33104867981f7bd44c649b907e683
tags: [domain/backend, stage/9, level/senior, topic/interview, topic/csharp, topic/dotnet, topic/quiz, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Частые вопросы C# и .NET: блиц

↑ [[BE 9.2 Финальная подготовка — проекты, live coding, вопросы|9.2 Финальная подготовка: проекты, live coding, вопросы]] · ← [[BE 9.2.4 Рассказ об observability и инфраструктуре (OTel, Docker, Makefile, Ansible)|Предыдущая]] · → [[BE 9.2.6 Задачи на лайв-кодинг — что выведет код, рефакторинг, написать эндпоинт|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Короткие вопросы для быстрого повторения перед интервью: отвечайте за 20–30 секунд.

## Язык и платформа

> [!question]- Value type и reference type?
> Value types (`struct`, `int`, `enum`) хранят значение, копируются при присваивании; reference types (`class`, `string`, массивы) хранят ссылку на объект в куче. Struct может лежать в стеке или внутри объекта.

> [!question]- Что такое boxing?
> Упаковка value type в `object` (аллокация в куче и копирование); обратная операция — unboxing. Дорого в горячих путях; избегают generic-ами.

> [!question]- `string` immutable — что это значит?
> Изменение создаёт новую строку. Для многократной конкатенации — `StringBuilder`.

> [!question]- Чем `==` отличается от `Equals`?
> `==` для ссылочных типов по умолчанию сравнивает ссылки (для `string` и `record` — значения), `Equals` можно переопределять.

> [!question]- `abstract class` или `interface`?
> Интерфейс — контракт (можно множественная реализация, default-методы), абстрактный класс — общее состояние и частичная реализация, одиночное наследование.

> [!question]- `readonly`, `const`, `static readonly`?
> `const` — константа времени компиляции; `readonly` — присваивается в конструкторе; `static readonly` — один раз при инициализации типа.

> [!question]- Что такое `record`?
> Ссылочный (или `record struct`) тип со значимой семантикой равенства, неизменяемостью по умолчанию, `with`-выражениями.

## Память и сборка мусора

> [!question]- Как работает GC?
> Поколения 0/1/2, куча больших объектов (LOH); собирает недостижимые объекты; поколение 0 собирается часто и быстро. Режимы: Workstation/Server, concurrent.

> [!question]- `IDisposable` и финализатор?
> `Dispose` детерминированно освобождает неуправляемые ресурсы (`using`); финализатор — страховка, замедляет GC. Шаблон: `Dispose(bool)` + `GC.SuppressFinalize`.

> [!question]- Утечки памяти в .NET — откуда?
> Подписки на события, статические коллекции, кэши без ограничения, не освобождённые `IDisposable`, замыкания, `HttpClient`-ошибки.

## Асинхронность

> [!question]- Что делает `await`?
> Освобождает поток на время ожидания, компилятор превращает метод в конечный автомат; продолжение выполняется после завершения задачи.

> [!question]- `Task` и `ValueTask`?
> `ValueTask` избегает аллокации при синхронном завершении; нельзя дважды `await` и хранить без осторожности.

> [!question]- `ConfigureAwait(false)`?
> Не возвращаться в исходный контекст; в библиотеках — желательно, в ASP.NET Core приложении — не нужно.

## Коллекции и LINQ

> [!question]- Отложенное выполнение LINQ?
> Запрос выполняется при переборе (`foreach`, `ToList`); повторный перебор пересчитывает; опасно при изменяемых источниках.

> [!question]- `IEnumerable` и `IQueryable`?
> `IEnumerable` работает в памяти (делегаты), `IQueryable` строит дерево выражений и транслируется провайдером (SQL).

> [!question]- `List<T>` и `T[]`?
> Массив фиксированного размера, список — динамический массив с амортизированным O(1) добавлением.

## ASP.NET Core и EF

> [!question]- Время жизни сервисов DI?
> Singleton, Scoped (на запрос), Transient; scoped в singleton — captive dependency.

> [!question]- Middleware и filters?
> Middleware — на уровне HTTP-конвейера; filters — внутри MVC/endpoint с контекстом action.

> [!question]- N+1 в EF Core?
> Запрос за списком и по запросу на каждую связь; решают `Include`, проекции, split queries.

> [!question]- `AsNoTracking`?
> Отключает отслеживание изменений: быстрее и меньше памяти для чтения.

## Многопоточность

> [!question]- `lock` и `SemaphoreSlim`?
> `lock` — эксклюзивный, синхронный, реентерабельный; `SemaphoreSlim` — счётчик, поддерживает `WaitAsync`, не реентерабелен.

> [!question]- Deadlock: как возникает?
> Взаимное ожидание ресурсов; в async — блокировка `.Result` при контексте синхронизации.

## Связанные темы

- [[N:3ea331048679811db22bed0c0fb1bb11]]
- [[N:3ea331048679810698b8cc309c958cbe]]
