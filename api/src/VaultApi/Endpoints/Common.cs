using System.Security.Claims;

namespace VaultApi.Endpoints;

public static class Common
{
    public static Guid UserId(this ClaimsPrincipal p) => Guid.Parse(p.FindFirstValue(ClaimTypes.NameIdentifier)!);

    // slug страницы: без слешей по краям, без управляющих символов, разумной длины
    public static string? NormalizeSlug(string? slug)
    {
        if (string.IsNullOrWhiteSpace(slug)) return null;
        var s = slug.Trim().Trim('/');
        if (s.Length == 0 || s.Length > 300 || s.Any(char.IsControl)) return null;
        return s;
    }

    public static IResult Bad(string error) => Results.BadRequest(new { error });
}
