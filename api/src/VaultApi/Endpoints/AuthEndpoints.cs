using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using VaultApi.Data;

namespace VaultApi.Endpoints;

public record RegisterRequest(string? Login, string? Password, string? Invite);
public record LoginRequest(string? Login, string? Password);
public record ChangePasswordRequest(string? Current, string? New);

public static partial class AuthEndpoints
{
    [GeneratedRegex("^[a-z0-9_.-]{3,32}$")]
    private static partial Regex LoginRx();

    public static string HashCode(string code) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(code.Trim())));

    static async Task SignIn(HttpContext ctx, User u)
    {
        var claims = new List<Claim>
        {
            new(ClaimTypes.NameIdentifier, u.Id.ToString()),
            new(ClaimTypes.Name, u.Login),
            new(ClaimTypes.Role, u.Role.ToString()),
            new("stamp", u.SecurityStamp.ToString()),
        };
        var id = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
        await ctx.SignInAsync(new ClaimsPrincipal(id), new AuthenticationProperties { IsPersistent = true });
    }

    static string? ValidatePassword(string? p) =>
        string.IsNullOrEmpty(p) || p.Length < 8 ? "Пароль: минимум 8 символов"
        : p.Length > 128 ? "Пароль: максимум 128 символов" : null;

    public static void MapAuth(this IEndpointRouteBuilder app)
    {
        var g = app.MapGroup("/api");

        g.MapPost("/auth/register", async (RegisterRequest r, AppDb db, IPasswordHasher<User> hasher, HttpContext ctx) =>
        {
            var login = r.Login?.Trim().ToLowerInvariant() ?? "";
            if (!LoginRx().IsMatch(login)) return Common.Bad("Логин: 3–32 символа, латиница, цифры и _ . -");
            if (ValidatePassword(r.Password) is { } pe) return Common.Bad(pe);
            if (string.IsNullOrWhiteSpace(r.Invite)) return Common.Bad("Нужен код приглашения");

            var hash = HashCode(r.Invite);
            var invite = await db.Invites.FirstOrDefaultAsync(i => i.CodeHash == hash);
            if (invite is null || invite.UsedById is not null || invite.ExpiresAt < DateTime.UtcNow)
                return Common.Bad("Приглашение недействительно или уже использовано");
            if (await db.Users.AnyAsync(u => u.Login == login)) return Common.Bad("Логин занят");

            var user = new User { Login = login, Role = Role.User };
            user.PasswordHash = hasher.HashPassword(user, r.Password!);
            db.Users.Add(user);
            invite.UsedById = user.Id;
            await db.SaveChangesAsync();
            await SignIn(ctx, user);
            return Results.Ok(new { user.Login, role = user.Role });
        }).RequireRateLimiting("auth");

        g.MapPost("/auth/login", async (LoginRequest r, AppDb db, IPasswordHasher<User> hasher, HttpContext ctx) =>
        {
            var login = r.Login?.Trim().ToLowerInvariant() ?? "";
            var user = await db.Users.FirstOrDefaultAsync(u => u.Login == login);
            // при неизвестном логине всё равно считаем хэш: время ответа не выдаёт, существует ли логин
            var res = hasher.VerifyHashedPassword(user ?? new User(), user?.PasswordHash ?? DummyHash, r.Password ?? "");
            if (user is null || user.IsBlocked || res == PasswordVerificationResult.Failed)
                return Results.Json(new { error = "Неверный логин или пароль" }, statusCode: 401);
            await SignIn(ctx, user);
            return Results.Ok(new { user.Login, role = user.Role });
        }).RequireRateLimiting("auth");

        g.MapPost("/auth/logout", async (HttpContext ctx) =>
        {
            await ctx.SignOutAsync();
            return Results.NoContent();
        });

        g.MapGet("/me", (ClaimsPrincipal p) => p.Identity?.IsAuthenticated == true
            ? Results.Ok(new { login = p.Identity.Name, role = p.FindFirstValue(ClaimTypes.Role) })
            : Results.NoContent()); // аноним: без ошибки, чтобы не шуметь в консоли браузера

        g.MapPost("/auth/password", async (ChangePasswordRequest r, ClaimsPrincipal p, AppDb db, IPasswordHasher<User> hasher, HttpContext ctx) =>
        {
            if (ValidatePassword(r.New) is { } pe) return Common.Bad(pe);
            var user = await db.Users.FindAsync(p.UserId());
            if (user is null) return Results.Unauthorized();
            if (hasher.VerifyHashedPassword(user, user.PasswordHash, r.Current ?? "") == PasswordVerificationResult.Failed)
                return Common.Bad("Текущий пароль неверный");
            user.PasswordHash = hasher.HashPassword(user, r.New!);
            user.SecurityStamp = Guid.NewGuid(); // все остальные сессии перестают действовать
            await db.SaveChangesAsync();
            await SignIn(ctx, user);
            return Results.NoContent();
        }).RequireAuthorization();
    }

    // валидный формат хэша ASP.NET Identity для несуществующего пользователя
    static readonly string DummyHash = new PasswordHasher<User>().HashPassword(new User(), Guid.NewGuid().ToString());
}
