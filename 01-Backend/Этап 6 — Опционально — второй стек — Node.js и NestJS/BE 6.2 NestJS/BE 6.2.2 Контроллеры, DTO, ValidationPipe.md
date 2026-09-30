---
type: topic
domain: backend
stage: 6
section: "6.2"
order: 2
status: todo
level: junior
notion_id: 3ea33104867981138808c8ece7b97ae7
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/nestjs, topic/validation, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Контроллеры, DTO, ValidationPipe

↑ [[BE 6.2 NestJS|6.2 NestJS]] · ← [[BE 6.2.1 Архитектура NestJS — модули, провайдеры, DI|Предыдущая]] · → [[BE 6.2.3 Guards, interceptors, pipes, exception filters|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->






















> [!info] Зачем это на собесе
> Как принимаются и проверяются данные в Nest: DTO и class-validator.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
export class CreateOrderDto {
  @IsString() @IsNotEmpty() @MaxLength(100) customer: string;
  @IsInt() @Min(1) @Max(1000) quantity: number;
  @IsEmail() email: string;
  @IsOptional() @IsEnum(Priority) priority?: Priority;
}

@Controller("orders")
export class OrdersController {
  constructor(private readonly orders: OrdersService) {}

  @Post()
  @HttpCode(201)
  create(@Body() dto: CreateOrderDto) { return this.orders.create(dto); }

  @Get(":id")
  find(@Param("id", ParseUUIDPipe) id: string) { return this.orders.find(id); }

  @Get()
  list(@Query() q: ListOrdersQuery) { return this.orders.list(q); }
}
```

Глобальная валидация:

```ts
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,              // убрать поля, не описанные в DTO
  forbidNonWhitelisted: true,   // 400 при лишних полях
  transform: true,              // приводить типы (строка → число) и создавать экземпляры DTO
}));
```

DTO — классы, а не интерфейсы: интерфейсы стираются при компиляции, и декораторы `class-validator` работают только на классах. Альтернативы: Zod/Valibot с пайпом.

## Нюансы и подводные камни

- Без `whitelist` в объект попадают любые поля (mass assignment).
- Вложенные объекты требуют `@ValidateNested()` и `@Type(() => Nested)`.
- Query-параметры приходят строками: нужен `transform: true` или `ParseIntPipe`.
- DTO для ответа тоже нужны: не отдавайте сущности БД (`ClassSerializerInterceptor`).
- Формат ошибок валидации стандартизируйте фильтром исключений.

## Практика

1. Опишите DTO создания и обновления (`PartialType`) заказа.
2. Включите `whitelist` и проверьте лишние поля.
3. Реализуйте валидацию вложенных позиций заказа.

## Вопросы с ответами

> [!question]- Что делает ValidationPipe?
> Проверяет входные данные по декораторам DTO и возвращает 400 при нарушении.

> [!question]- Зачем whitelist?
> Отбрасывает или запрещает поля, не описанные в DTO, защищая от mass assignment.

## Связанные темы

- [[N:3ea33104867981c0b1f6cbbaf8a20394]]
- [[N:3ea331048679817d8d0cd3de6fc0a1af]]
