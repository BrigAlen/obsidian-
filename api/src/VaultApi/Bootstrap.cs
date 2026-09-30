using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using VaultApi.Data;

namespace VaultApi;

public static class Bootstrap
{
    // Миграции и первый администратор из ADMIN_LOGIN / ADMIN_PASSWORD (если пользователей ещё нет)
    public static async Task RunAsync(IServiceProvider sp, IConfiguration cfg)
    {
        var db = sp.GetRequiredService<AppDb>();
        await db.Database.MigrateAsync();

        if (await db.Users.AnyAsync()) return;
        var login = cfg["ADMIN_LOGIN"];
        var password = cfg["ADMIN_PASSWORD"];
        if (string.IsNullOrWhiteSpace(login) || string.IsNullOrEmpty(password)) return;

        if (password.Length < 8)
            sp.GetRequiredService<ILoggerFactory>().CreateLogger("Bootstrap")
                .LogWarning("ADMIN_PASSWORD короче 8 символов: смените пароль после первого входа");

        var hasher = sp.GetRequiredService<IPasswordHasher<User>>();
        var admin = new User { Login = login.Trim().ToLowerInvariant(), Role = Role.Admin };
        admin.PasswordHash = hasher.HashPassword(admin, password);
        db.Users.Add(admin);
        await db.SaveChangesAsync();
    }
}
