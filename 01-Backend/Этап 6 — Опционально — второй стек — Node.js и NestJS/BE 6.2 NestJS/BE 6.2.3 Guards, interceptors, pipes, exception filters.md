---
type: topic
domain: backend
stage: 6
section: "6.2"
order: 3
status: todo
level: junior
notion_id: 3ea331048679817d8d0cd3de6fc0a1af
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/nestjs, topic/pipeline, priority/nice]
reviewed:
next_review:
priority: nice
time: 4
---

# Guards, interceptors, pipes, exception filters

↑ [[BE 6.2 NestJS|6.2 NestJS]] · ← [[BE 6.2.2 Контроллеры, DTO, ValidationPipe|Предыдущая]] · → [[BE 6.2.4 Конфигурация, аутентификация (Passport, JWT), Swagger|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->
































> [!info] Зачем это на собесе
> Порядок обработки запроса в Nest и роль каждого компонента.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Порядок: middleware → guards → interceptors (до) → pipes → handler → interceptors (после) → exception filters.

| Компонент | Назначение | Аналог в ASP.NET Core |
|---|---|---|
| Middleware | низкоуровневая обработка запроса | middleware |
| Guard | разрешить/запретить (`canActivate`) | authorization filter/policy |
| Interceptor | обернуть выполнение: логирование, кэш, преобразование ответа, таймаут | action/result filter |
| Pipe | преобразование и валидация параметров | model binding + validation |
| Exception filter | преобразование исключения в ответ | `IExceptionHandler` |

```ts
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}
  canActivate(ctx: ExecutionContext): boolean {
    const roles = this.reflector.get<string[]>("roles", ctx.getHandler());
    const user = ctx.switchToHttp().getRequest().user;
    return !roles || roles.some(r => user?.roles?.includes(r));
  }
}

@Injectable()
export class TimingInterceptor implements NestInterceptor {
  intercept(_: ExecutionContext, next: CallHandler) {
    const t = Date.now();
    return next.handle().pipe(tap(() => console.log(`${Date.now() - t} ms`)));
  }
}

@Catch(HttpException)
export class HttpErrorFilter implements ExceptionFilter {
  catch(e: HttpException, host: ArgumentsHost) {
    const res = host.switchToHttp().getResponse();
    res.status(e.getStatus()).json({ status: e.getStatus(), message: e.message });
  }
}

@UseGuards(JwtAuthGuard, RolesGuard)
@UseInterceptors(TimingInterceptor)
@Get("admin") admin() {}
```

Применение: на метод, контроллер или глобально (`app.useGlobalGuards`, провайдеры `APP_GUARD`).

## Нюансы и подводные камни

- Глобальные guards, зарегистрированные через `app.use…`, не получают DI: используйте `APP_GUARD`.
- Порядок декораторов и уровней (global → controller → method) важен.
- Исключения вне HTTP-контекста (микросервисы, WebSocket) требуют своих фильтров.
- Не помещайте бизнес-логику в interceptor.

## Практика

1. Реализуйте роль-guard с кастомным декоратором `@Roles()`.
2. Сделайте interceptor кэширования ответов.
3. Единый фильтр ошибок с `traceId`.

## Вопросы с ответами

> [!question]- Чем guard отличается от middleware?
> Guard знает о контексте исполнения (какой handler будет вызван) и решает доступ, middleware — нет.

> [!question]- Что делает interceptor?
> Оборачивает вызов handler: код до и после, преобразование результата и ошибок.

## Связанные темы

- [[N:3ea33104867981138808c8ece7b97ae7]]
- [[N:3ea331048679814ba0c1f776ed6aad25]]
