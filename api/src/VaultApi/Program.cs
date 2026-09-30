using Microsoft.AspNetCore.Authentication;
using System.Security.Claims;
using System.Threading.RateLimiting;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.HttpOverrides;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using VaultApi;
using VaultApi.Data;
using VaultApi.Endpoints;

var builder = WebApplication.CreateBuilder(args);

// Render передаёт порт в переменной PORT
if (Environment.GetEnvironmentVariable("PORT") is { Length: > 0 } port)
    builder.WebHost.UseUrls($"http://+:{port}");

var conn = builder.Configuration["DATABASE_URL"]
    ?? builder.Configuration.GetConnectionString("Default")
    ?? throw new InvalidOperationException("Не задана строка подключения: переменная DATABASE_URL");
builder.Services.AddDbContext<AppDb>(o => o.UseNpgsql(DbConfig.ToNpgsql(conn)));

builder.Services.AddSingleton<IPasswordHasher<User>, PasswordHasher<User>>();

builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(o =>
    {
        o.Cookie.Name = "vault.sid";
        o.Cookie.HttpOnly = true;
        o.Cookie.SameSite = SameSiteMode.Strict;
        o.Cookie.SecurePolicy = CookieSecurePolicy.SameAsRequest;
        o.ExpireTimeSpan = TimeSpan.FromDays(30);
        o.SlidingExpiration = true;
        // для API вместо редиректа на страницу входа отдаём статус
        o.Events.OnRedirectToLogin = c => { c.Response.StatusCode = 401; return Task.CompletedTask; };
        o.Events.OnRedirectToAccessDenied = c => { c.Response.StatusCode = 403; return Task.CompletedTask; };
        // сессия недействительна, если пользователь заблокирован или сменился пароль
        o.Events.OnValidatePrincipal = async c =>
        {
            var id = c.Principal?.FindFirstValue(ClaimTypes.NameIdentifier);
            var stamp = c.Principal?.FindFirstValue("stamp");
            var db = c.HttpContext.RequestServices.GetRequiredService<AppDb>();
            var ok = Guid.TryParse(id, out var uid)
                && await db.Users.AnyAsync(u => u.Id == uid && !u.IsBlocked && u.SecurityStamp.ToString() == stamp);
            if (!ok)
            {
                c.RejectPrincipal();
                await c.HttpContext.SignOutAsync();
            }
        };
    });
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("Admin", p => p.RequireRole(nameof(Role.Admin)));

builder.Services.AddRateLimiter(o =>
{
    o.RejectionStatusCode = 429;
    // вход и регистрация: защита от перебора пароля и кодов приглашений
    o.AddPolicy("auth", ctx => RateLimitPartition.GetFixedWindowLimiter(
        ctx.Connection.RemoteIpAddress?.ToString() ?? "?",
        _ => new FixedWindowRateLimiterOptions { PermitLimit = builder.Configuration.GetValue("AUTH_RATE_LIMIT", 10), Window = TimeSpan.FromMinutes(1) }));
});

builder.Services.Configure<ForwardedHeadersOptions>(o =>
{
    o.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    o.KnownIPNetworks.Clear();
    o.KnownProxies.Clear();
});

builder.Services.ConfigureHttpJsonOptions(o => o.SerializerOptions.Converters.Add(new System.Text.Json.Serialization.JsonStringEnumConverter(System.Text.Json.JsonNamingPolicy.CamelCase)));

var app = builder.Build();

app.UseForwardedHeaders();

// Применяем миграции и создаём администратора при первом запуске
await using (var scope = app.Services.CreateAsyncScope())
{
    await Bootstrap.RunAsync(scope.ServiceProvider, app.Configuration);
}

app.UseRateLimiter();
app.UseAuthentication();
app.UseAuthorization();

// Защита от CSRF: изменяющие запросы к API обязаны нести заголовок, которого не отправит чужая форма
app.Use(async (ctx, next) =>
{
    if (ctx.Request.Path.StartsWithSegments("/api")
        && !HttpMethods.IsGet(ctx.Request.Method) && !HttpMethods.IsHead(ctx.Request.Method)
        && ctx.Request.Headers["X-Requested-With"] != "vault")
    {
        ctx.Response.StatusCode = 400;
        await ctx.Response.WriteAsJsonAsync(new { error = "missing X-Requested-With" });
        return;
    }
    await next();
});

app.MapGet("/healthz", () => Results.Ok(new { status = "ok" }));
app.MapAuth();
app.MapProgress();
app.MapNotes();
app.MapAdmin();
app.MapBacklog();
app.MapGroup("/api").MapFallback(() => Results.NotFound());

// Сайт (Quartz) лежит в wwwroot: поддерживаем «чистые» адреса без .html
app.UseMiddleware<CleanUrlMiddleware>();
app.UseStaticFiles();
app.Use(async (ctx, next) =>
{
    await next();
    if (ctx.Response.StatusCode == 404 && !ctx.Response.HasStarted && !ctx.Request.Path.StartsWithSegments("/api"))
    {
        var page = Path.Combine(app.Environment.WebRootPath ?? "", "404.html");
        if (File.Exists(page))
        {
            ctx.Response.ContentType = "text/html; charset=utf-8";
            await ctx.Response.SendFileAsync(page);
        }
    }
});

app.Run();

public partial class Program;
