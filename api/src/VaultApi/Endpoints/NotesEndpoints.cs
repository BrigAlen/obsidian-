using System.Security.Claims;
using Microsoft.EntityFrameworkCore;
using VaultApi.Data;

namespace VaultApi.Endpoints;

public record NoteRequest(string? Slug, string? Title, string? Body);

public static class NotesEndpoints
{
    const int MaxBody = 20000;

    public static void MapNotes(this IEndpointRouteBuilder app)
    {
        var g = app.MapGroup("/api/notes").RequireAuthorization();

        // общий список заметок (с темой) или заметки одной темы: ?slug=...; поиск ?q=...
        g.MapGet("/", async (ClaimsPrincipal p, AppDb db, string? slug, string? q, int? skip, int? take) =>
        {
            var uid = p.UserId();
            var query = db.Notes.Where(n => n.UserId == uid);
            if (Common.NormalizeSlug(slug) is { } s) query = query.Where(n => n.TopicSlug == s);
            if (!string.IsNullOrWhiteSpace(q))
            {
                var like = $"%{q.Trim().Replace("\\", "\\\\").Replace("%", "\\%").Replace("_", "\\_")}%";
                query = query.Where(n => EF.Functions.ILike(n.Body, like) || EF.Functions.ILike(n.TopicTitle, like));
            }
            var total = await query.CountAsync();
            var items = await query.OrderByDescending(n => n.UpdatedAt)
                .Skip(Math.Max(skip ?? 0, 0)).Take(Math.Clamp(take ?? 50, 1, 100))
                .Select(n => new { n.Id, slug = n.TopicSlug, title = n.TopicTitle, n.Body, n.CreatedAt, n.UpdatedAt })
                .ToListAsync();
            return Results.Ok(new { total, items });
        });

        g.MapPost("/", async (NoteRequest r, ClaimsPrincipal p, AppDb db) =>
        {
            var slug = Common.NormalizeSlug(r.Slug);
            if (slug is null) return Common.Bad("Некорректный адрес темы");
            if (string.IsNullOrWhiteSpace(r.Body)) return Common.Bad("Пустая заметка");
            if (r.Body.Length > MaxBody) return Common.Bad($"Заметка длиннее {MaxBody} символов");
            var note = new Note
            {
                UserId = p.UserId(), TopicSlug = slug,
                TopicTitle = (r.Title ?? slug).Trim()[..Math.Min((r.Title ?? slug).Trim().Length, 300)],
                Body = r.Body,
            };
            db.Notes.Add(note);
            await db.SaveChangesAsync();
            return Results.Created($"/api/notes/{note.Id}", new { note.Id, slug = note.TopicSlug, title = note.TopicTitle, note.Body, note.CreatedAt, note.UpdatedAt });
        });

        g.MapPut("/{id:guid}", async (Guid id, NoteRequest r, ClaimsPrincipal p, AppDb db) =>
        {
            var uid = p.UserId();
            var note = await db.Notes.FirstOrDefaultAsync(n => n.Id == id && n.UserId == uid);
            if (note is null) return Results.NotFound();
            if (string.IsNullOrWhiteSpace(r.Body)) return Common.Bad("Пустая заметка");
            if (r.Body.Length > MaxBody) return Common.Bad($"Заметка длиннее {MaxBody} символов");
            note.Body = r.Body;
            note.UpdatedAt = DateTime.UtcNow;
            await db.SaveChangesAsync();
            return Results.Ok(new { note.Id, slug = note.TopicSlug, title = note.TopicTitle, note.Body, note.CreatedAt, note.UpdatedAt });
        });

        g.MapDelete("/{id:guid}", async (Guid id, ClaimsPrincipal p, AppDb db) =>
        {
            var uid = p.UserId();
            var n = await db.Notes.Where(x => x.Id == id && x.UserId == uid).ExecuteDeleteAsync();
            return n == 0 ? Results.NotFound() : Results.NoContent();
        });
    }
}
