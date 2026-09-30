using System.Security.Claims;
using System.Security.Cryptography;
using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using VaultApi.Data;

namespace VaultApi.Endpoints;

public record ResetPasswordRequest(string? Password);

public static class AdminEndpoints
{
    public static void MapAdmin(this IEndpointRouteBuilder app)
    {
        var g = app.MapGroup("/api/admin").RequireAuthorization("Admin");

        // одноразовый код приглашения; показывается один раз, в базе только хэш
        g.MapPost("/invites", async (ClaimsPrincipal p, AppDb db, int? days) =>
        {
            var code = Convert.ToBase64String(RandomNumberGenerator.GetBytes(18)).Replace('+', '-').Replace('/', '_');
            db.Invites.Add(new Invite
            {
                CodeHash = AuthEndpoints.HashCode(code),
                CreatedById = p.UserId(),
                ExpiresAt = DateTime.UtcNow.AddDays(Math.Clamp(days ?? 7, 1, 60)),
            });
            await db.SaveChangesAsync();
            return Results.Ok(new { code });
        });

        g.MapGet("/users", async (AppDb db) => Results.Ok(await db.Users.OrderBy(u => u.CreatedAt)
            .Select(u => new { u.Id, u.Login, role = u.Role, u.IsBlocked, u.CreatedAt }).ToListAsync()));

        g.MapPost("/users/{id:guid}/reset-password", async (Guid id, ResetPasswordRequest r, AppDb db, IPasswordHasher<User> hasher) =>
        {
            if (string.IsNullOrEmpty(r.Password) || r.Password.Length < 8) return Common.Bad("Пароль: минимум 8 символов");
            var u = await db.Users.FindAsync(id);
            if (u is null) return Results.NotFound();
            u.PasswordHash = hasher.HashPassword(u, r.Password);
            u.SecurityStamp = Guid.NewGuid();
            await db.SaveChangesAsync();
            return Results.NoContent();
        });

        g.MapPost("/users/{id:guid}/block", async (Guid id, bool blocked, ClaimsPrincipal p, AppDb db) =>
        {
            if (id == p.UserId()) return Common.Bad("Нельзя заблокировать себя");
            var u = await db.Users.FindAsync(id);
            if (u is null) return Results.NotFound();
            u.IsBlocked = blocked;
            await db.SaveChangesAsync();
            return Results.NoContent();
        });
    }
}
