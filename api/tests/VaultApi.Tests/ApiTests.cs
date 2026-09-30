using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;

namespace VaultApi.Tests;

public class Factory : WebApplicationFactory<Program>
{
    public Factory()
    {
        // отдельная база на каждый запуск, чтобы тесты не мешали друг другу
        Db = $"vault_test_{Guid.NewGuid():N}";
        Environment.SetEnvironmentVariable("DATABASE_URL",
            $"Host=localhost;Database={Db};Username=vault;Password=vault");
        var backlog = Path.Combine(Path.GetTempPath(), $"backlog_{Guid.NewGuid():N}.md");
        File.WriteAllText(backlog, "---\ntitle: Бэклог\ndraft: true\n---\n\n# Бэклог\n\n- [ ] Задача про [[Страница|ссылку]]\n");
        Environment.SetEnvironmentVariable("BACKLOG_PATH", backlog);
        Environment.SetEnvironmentVariable("AUTH_RATE_LIMIT", "1000");
        Environment.SetEnvironmentVariable("ADMIN_LOGIN", "admin");
        Environment.SetEnvironmentVariable("ADMIN_PASSWORD", "admin-pass-1");
    }

    public string Db { get; }

    protected override void Dispose(bool disposing)
    {
        base.Dispose(disposing);
        if (!disposing) return;
        using var c = new Npgsql.NpgsqlConnection("Host=localhost;Database=postgres;Username=vault;Password=vault");
        c.Open();
        using var cmd = c.CreateCommand();
        cmd.CommandText = $"DROP DATABASE IF EXISTS {Db} WITH (FORCE)";
        cmd.ExecuteNonQuery();
    }

    protected override void ConfigureWebHost(IWebHostBuilder builder) => builder.UseEnvironment("Testing");

    public HttpClient NewClient()
    {
        var c = CreateClient(new WebApplicationFactoryClientOptions { HandleCookies = true });
        c.DefaultRequestHeaders.Add("X-Requested-With", "vault");
        return c;
    }
}

public class ApiTests : IClassFixture<Factory>
{
    readonly Factory f;
    public ApiTests(Factory f) => this.f = f;

    static async Task<JsonElement> Json(HttpResponseMessage r) =>
        JsonDocument.Parse(await r.Content.ReadAsStringAsync()).RootElement;

    async Task<HttpClient> AdminAsync()
    {
        var c = f.NewClient();
        var r = await c.PostAsJsonAsync("/api/auth/login", new { login = "admin", password = "admin-pass-1" });
        Assert.Equal(HttpStatusCode.OK, r.StatusCode);
        return c;
    }

    async Task<HttpClient> UserAsync(string login)
    {
        var admin = await AdminAsync();
        var code = (await Json(await admin.PostAsync("/api/admin/invites", null))).GetProperty("code").GetString();
        var c = f.NewClient();
        var r = await c.PostAsJsonAsync("/api/auth/register", new { login, password = "password-1", invite = code });
        Assert.Equal(HttpStatusCode.OK, r.StatusCode);
        return c;
    }

    [Fact]
    public async Task Anonymous_is_rejected()
    {
        var c = f.NewClient();
        Assert.Equal(HttpStatusCode.NoContent, (await c.GetAsync("/api/me")).StatusCode);
        Assert.Equal(HttpStatusCode.Unauthorized, (await c.GetAsync("/api/progress")).StatusCode);
        Assert.Equal(HttpStatusCode.Unauthorized, (await c.GetAsync("/api/notes")).StatusCode);
    }

    [Fact]
    public async Task Mutations_require_csrf_header()
    {
        var c = f.CreateClient();
        var r = await c.PostAsJsonAsync("/api/auth/login", new { login = "admin", password = "admin-pass-1" });
        Assert.Equal(HttpStatusCode.BadRequest, r.StatusCode);
    }

    [Fact]
    public async Task Wrong_password_is_401()
    {
        var c = f.NewClient();
        var r = await c.PostAsJsonAsync("/api/auth/login", new { login = "admin", password = "nope" });
        Assert.Equal(HttpStatusCode.Unauthorized, r.StatusCode);
    }

    [Fact]
    public async Task Register_needs_valid_one_time_invite()
    {
        var c = f.NewClient();
        var bad = await c.PostAsJsonAsync("/api/auth/register", new { login = "bob", password = "password-1", invite = "wrong" });
        Assert.Equal(HttpStatusCode.BadRequest, bad.StatusCode);

        var admin = await AdminAsync();
        var code = (await Json(await admin.PostAsync("/api/admin/invites", null))).GetProperty("code").GetString();
        var ok = await c.PostAsJsonAsync("/api/auth/register", new { login = "bob", password = "password-1", invite = code });
        Assert.Equal(HttpStatusCode.OK, ok.StatusCode);
        Assert.Equal("bob", (await Json(await c.GetAsync("/api/me"))).GetProperty("login").GetString());

        // второй раз тот же код не работает
        var again = await f.NewClient().PostAsJsonAsync("/api/auth/register", new { login = "bob2", password = "password-1", invite = code });
        Assert.Equal(HttpStatusCode.BadRequest, again.StatusCode);
    }

    [Fact]
    public async Task Regular_user_cannot_use_admin_api()
    {
        var u = await UserAsync("carol");
        Assert.Equal(HttpStatusCode.Forbidden, (await u.PostAsync("/api/admin/invites", null)).StatusCode);
        Assert.Equal(HttpStatusCode.Forbidden, (await u.GetAsync("/api/admin/users")).StatusCode);
    }

    [Fact]
    public async Task Progress_set_list_and_clear()
    {
        var u = await UserAsync("dave");
        await u.PutAsJsonAsync("/api/progress", new { slug = "/01-backend/stage-1/x/", status = "done" });
        await u.PutAsJsonAsync("/api/progress", new { slug = "01-backend/stage-1/y", status = "inProgress" });
        var j = await Json(await u.GetAsync("/api/progress"));
        Assert.Equal(1, j.GetProperty("done").GetInt32());
        Assert.Equal(1, j.GetProperty("inProgress").GetInt32());
        Assert.Contains(j.GetProperty("items").EnumerateArray(), i => i.GetProperty("slug").GetString() == "01-backend/stage-1/x");

        await u.PutAsJsonAsync("/api/progress", new { slug = "01-backend/stage-1/x", status = "todo" });
        Assert.Equal(0, (await Json(await u.GetAsync("/api/progress"))).GetProperty("done").GetInt32());
    }

    [Fact]
    public async Task Notes_crud_search_and_isolation()
    {
        var a = await UserAsync("erin");
        var b = await UserAsync("frank");

        var created = await a.PostAsJsonAsync("/api/notes", new { slug = "01-backend/t1", title = "Тема 1", body = "про async/await" });
        Assert.Equal(HttpStatusCode.Created, created.StatusCode);
        var id = (await Json(created)).GetProperty("id").GetString();
        await a.PostAsJsonAsync("/api/notes", new { slug = "02-frontend/t2", title = "Тема 2", body = "про реактивность" });

        var all = await Json(await a.GetAsync("/api/notes"));
        Assert.Equal(2, all.GetProperty("total").GetInt32());
        Assert.Contains(all.GetProperty("items").EnumerateArray(), n => n.GetProperty("title").GetString() == "Тема 1");

        var found = await Json(await a.GetAsync("/api/notes?q=async"));
        Assert.Equal(1, found.GetProperty("total").GetInt32());
        Assert.Equal(1, (await Json(await a.GetAsync("/api/notes?slug=02-frontend/t2"))).GetProperty("total").GetInt32());

        // чужие заметки не видны и не меняются
        Assert.Equal(0, (await Json(await b.GetAsync("/api/notes"))).GetProperty("total").GetInt32());
        Assert.Equal(HttpStatusCode.NotFound, (await b.PutAsJsonAsync($"/api/notes/{id}", new { body = "взлом" })).StatusCode);
        Assert.Equal(HttpStatusCode.NotFound, (await b.DeleteAsync($"/api/notes/{id}")).StatusCode);

        Assert.Equal(HttpStatusCode.OK, (await a.PutAsJsonAsync($"/api/notes/{id}", new { body = "правка" })).StatusCode);
        Assert.Equal(HttpStatusCode.NoContent, (await a.DeleteAsync($"/api/notes/{id}")).StatusCode);
        Assert.Equal(1, (await Json(await a.GetAsync("/api/notes"))).GetProperty("total").GetInt32());
    }

    [Fact]
    public async Task Password_change_invalidates_other_sessions()
    {
        var u = await UserAsync("grace");
        var other = f.NewClient();
        await other.PostAsJsonAsync("/api/auth/login", new { login = "grace", password = "password-1" });
        Assert.Equal(HttpStatusCode.OK, (await other.GetAsync("/api/me")).StatusCode);

        var r = await u.PostAsJsonAsync("/api/auth/password", new { current = "password-1", @new = "password-2" });
        Assert.Equal(HttpStatusCode.NoContent, r.StatusCode);
        Assert.Equal(HttpStatusCode.OK, (await u.GetAsync("/api/me")).StatusCode);
        Assert.Equal(HttpStatusCode.NoContent, (await other.GetAsync("/api/me")).StatusCode);
    }

    [Fact]
    public async Task Blocked_user_loses_access()
    {
        var u = await UserAsync("heidi");
        var admin = await AdminAsync();
        var users = await Json(await admin.GetAsync("/api/admin/users"));
        var id = users.EnumerateArray().First(x => x.GetProperty("login").GetString() == "heidi").GetProperty("id").GetString();
        Assert.Equal(HttpStatusCode.NoContent, (await admin.PostAsync($"/api/admin/users/{id}/block?blocked=true", null)).StatusCode);
        Assert.Equal(HttpStatusCode.NoContent, (await u.GetAsync("/api/me")).StatusCode);
        var r = await f.NewClient().PostAsJsonAsync("/api/auth/login", new { login = "heidi", password = "password-1" });
        Assert.Equal(HttpStatusCode.Unauthorized, r.StatusCode);
    }

    [Fact]
    public async Task Backlog_page_is_admin_only()
    {
        Assert.Equal(HttpStatusCode.NotFound, (await f.NewClient().GetAsync("/admin/backlog")).StatusCode);
        var user = await UserAsync("ivan");
        Assert.Equal(HttpStatusCode.NotFound, (await user.GetAsync("/admin/backlog")).StatusCode);

        var admin = await AdminAsync();
        var r = await admin.GetAsync("/admin/backlog");
        Assert.Equal(HttpStatusCode.OK, r.StatusCode);
        var html = await r.Content.ReadAsStringAsync();
        Assert.Contains("<h1", html);
        Assert.Contains("Задача про ссылку", html);   // wiki-ссылка заменена подписью
        Assert.DoesNotContain("draft: true", html);    // frontmatter убран
    }

    [Fact]
    public async Task Health_is_open()
    {
        Assert.Equal(HttpStatusCode.OK, (await f.NewClient().GetAsync("/healthz")).StatusCode);
    }
}
