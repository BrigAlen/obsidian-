using System.Security.Claims;
using Microsoft.EntityFrameworkCore;
using VaultApi.Data;

namespace VaultApi.Endpoints;

public record SetProgressRequest(string? Slug, TopicStatus Status);

public static class ProgressEndpoints
{
    public static void MapProgress(this IEndpointRouteBuilder app)
    {
        var g = app.MapGroup("/api/progress").RequireAuthorization();

        // все отметки пользователя: {slug, status, updatedAt}
        g.MapGet("/", async (ClaimsPrincipal p, AppDb db) =>
        {
            var uid = p.UserId();
            var items = await db.Progress.Where(x => x.UserId == uid)
                .OrderByDescending(x => x.UpdatedAt)
                .Select(x => new { slug = x.TopicSlug, status = x.Status, updatedAt = x.UpdatedAt })
                .ToListAsync();
            return Results.Ok(new
            {
                items,
                done = items.Count(i => i.status == TopicStatus.Done),
                inProgress = items.Count(i => i.status == TopicStatus.InProgress),
            });
        });

        // установить статус темы; Todo снимает отметку
        g.MapPut("/", async (SetProgressRequest r, ClaimsPrincipal p, AppDb db) =>
        {
            var slug = Common.NormalizeSlug(r.Slug);
            if (slug is null) return Common.Bad("Некорректный адрес темы");
            if (!Enum.IsDefined(r.Status)) return Common.Bad("Некорректный статус");
            var uid = p.UserId();
            var row = await db.Progress.FindAsync(uid, slug);
            if (r.Status == TopicStatus.Todo)
            {
                if (row is not null) db.Progress.Remove(row);
            }
            else if (row is null)
            {
                db.Progress.Add(new Progress { UserId = uid, TopicSlug = slug, Status = r.Status });
            }
            else
            {
                row.Status = r.Status;
                row.UpdatedAt = DateTime.UtcNow;
            }
            await db.SaveChangesAsync();
            return Results.NoContent();
        });
    }
}
