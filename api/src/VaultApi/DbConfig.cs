using Npgsql;

namespace VaultApi;

public static class DbConfig
{
    // Render/Neon отдают строку вида postgresql://user:pass@host/db?sslmode=require,
    // Npgsql ждёт формат «ключ=значение»; принимаем оба.
    public static string ToNpgsql(string raw)
    {
        if (!raw.StartsWith("postgres://") && !raw.StartsWith("postgresql://"))
            return raw;
        var u = new Uri(raw);
        var userInfo = u.UserInfo.Split(':', 2);
        var b = new NpgsqlConnectionStringBuilder
        {
            Host = u.Host,
            Port = u.Port > 0 ? u.Port : 5432,
            Database = u.AbsolutePath.TrimStart('/'),
            Username = Uri.UnescapeDataString(userInfo[0]),
            Password = userInfo.Length > 1 ? Uri.UnescapeDataString(userInfo[1]) : null,
            SslMode = SslMode.Require,
        };
        return b.ConnectionString;
    }
}
