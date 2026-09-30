---
type: topic
domain: backend
stage: 6
section: "6.2"
order: 4
status: todo
level: junior
notion_id: 3ea331048679814ba0c1f776ed6aad25
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/nestjs, topic/auth, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Конфигурация, аутентификация (Passport, JWT), Swagger

↑ [[BE 6.2 NestJS|6.2 NestJS]] · ← [[BE 6.2.3 Guards, interceptors, pipes, exception filters|Предыдущая]] · → [[BE 6.2.5 NestJS и ASP.NET Core — сравнение концепций|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->
































> [!info] Зачем это на собесе
> Типовая связка для настоящего Nest-проекта: конфиг, JWT и документация.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### Конфигурация

```ts
ConfigModule.forRoot({
  isGlobal: true,
  validate: (env) => envSchema.parse(env),     // fail fast при отсутствии переменных (zod/joi)
});
// использование
constructor(private cfg: ConfigService<Env, true>) { const url = cfg.get("DATABASE_URL", { infer: true }); }
```

Переменные окружения — основной источник; `.env` только локально.

### JWT и Passport

```ts
@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(cfg: ConfigService) {
    super({ jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(), secretOrKey: cfg.get("JWT_SECRET") });
  }
  validate(payload: { sub: string; roles: string[] }) { return { id: payload.sub, roles: payload.roles }; }
}

@Injectable() export class JwtAuthGuard extends AuthGuard("jwt") {}

// выдача токена
const token = await this.jwt.signAsync({ sub: user.id, roles: user.roles }, { expiresIn: "15m" });
```

Стратегии Passport: `local` (логин/пароль), `jwt`, OAuth-провайдеры. Пароли — `argon2`/`bcrypt`.

### Swagger

```ts
const doc = SwaggerModule.createDocument(app, new DocumentBuilder().setTitle("Orders").addBearerAuth().build());
SwaggerModule.setup("docs", app, doc);
```

Плагин `@nestjs/swagger` выводит схемы из DTO; декораторы `@ApiProperty`, `@ApiResponse` уточняют описание.

## Нюансы и подводные камни

- Секрет JWT не в коде; для распределённых систем — асимметричные ключи и JWKS.
- Refresh-токены храните безопасно и ротируйте.
- Swagger в проде закрывайте или отключайте.
- `secretOrKey` из конфигурации проверяйте при старте.

## Практика

1. Реализуйте регистрацию, логин и защищённый эндпоинт с JWT.
2. Валидируйте переменные окружения через zod.
3. Опишите API в Swagger и сгенерируйте клиент.

## Вопросы с ответами

> [!question]- Как в Nest защитить эндпоинт JWT?
> Стратегия `passport-jwt` + `AuthGuard("jwt")` через `@UseGuards`.

> [!question]- Зачем валидировать конфигурацию при старте?
> Приложение падает сразу при неверной настройке вместо ошибок в рантайме.

## Связанные темы

- [[N:3ea331048679817d8d0cd3de6fc0a1af]]
- [[N:3ea33104867981eab321da100aae4744]]
