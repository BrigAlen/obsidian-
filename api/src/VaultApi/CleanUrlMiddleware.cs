namespace VaultApi;

// /01-backend/stage-1/x -> x.html, /01-backend/ -> /01-backend/index.html
public class CleanUrlMiddleware(RequestDelegate next, IWebHostEnvironment env)
{
    public async Task InvokeAsync(HttpContext ctx)
    {
        var path = ctx.Request.Path.Value ?? "/";
        if ((HttpMethods.IsGet(ctx.Request.Method) || HttpMethods.IsHead(ctx.Request.Method))
            && !path.StartsWith("/api") && string.IsNullOrEmpty(Path.GetExtension(path)) && env.WebRootPath is { } root)
        {
            var rel = Uri.UnescapeDataString(path).TrimStart('/');
            if (!rel.Contains(".."))
            {
                if (File.Exists(Path.Combine(root, rel + ".html")))
                    ctx.Request.Path = path + ".html";
                else if (Directory.Exists(Path.Combine(root, rel)) && File.Exists(Path.Combine(root, rel, "index.html")))
                    ctx.Request.Path = path.TrimEnd('/') + "/index.html";
            }
        }
        await next(ctx);
    }
}
