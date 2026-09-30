using System.Net;
using System.Security.Claims;
using System.Text.RegularExpressions;
using Markdig;

namespace VaultApi.Endpoints;

// Бэклог — заметка vault, которую на публичный сайт не выкладываем (draft: true).
// Администратору она отдаётся отдельной страницей /admin/backlog, остальным — 404.
public static partial class BacklogEndpoints
{
    static readonly MarkdownPipeline Pipeline = new MarkdownPipelineBuilder()
        .UseAdvancedExtensions().DisableHtml().Build();

    [GeneratedRegex(@"\[\[([^\]|]+)(?:\|([^\]]*))?\]\]")]
    private static partial Regex WikiLink();

    public static void MapBacklog(this IEndpointRouteBuilder app)
    {
        app.MapGet("/admin/backlog", (ClaimsPrincipal user, IConfiguration cfg, IWebHostEnvironment env) =>
        {
            if (user.Identity?.IsAuthenticated != true || !user.IsInRole("Admin"))
                return Results.NotFound();

            var path = cfg["BACKLOG_PATH"] ?? Path.Combine(AppContext.BaseDirectory, "private", "backlog.md");
            if (!File.Exists(path)) return Results.NotFound();

            var md = File.ReadAllText(path);
            md = Regex.Replace(md, @"\A---\n.*?\n---\n", "", RegexOptions.Singleline);        // frontmatter
            md = WikiLink().Replace(md, m => m.Groups[2].Success && m.Groups[2].Value.Length > 0 ? m.Groups[2].Value : m.Groups[1].Value);
            var body = Markdown.ToHtml(md, Pipeline);

            var html = $$"""
                <!doctype html>
                <html lang="ru"><head>
                <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
                <meta name="robots" content="noindex">
                <title>Бэклог</title>
                <link rel="stylesheet" href="/index.css"><link rel="stylesheet" href="/app.css">
                </head><body>
                <main class="private-page"><p><a href="/">← На сайт</a></p><article>{{body}}</article></main>
                </body></html>
                """;
            return Results.Content(html, "text/html; charset=utf-8");
        });
    }
}
