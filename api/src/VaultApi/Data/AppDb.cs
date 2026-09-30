using Microsoft.EntityFrameworkCore;

namespace VaultApi.Data;

public class AppDb(DbContextOptions<AppDb> options) : DbContext(options)
{
    public DbSet<User> Users => Set<User>();
    public DbSet<Invite> Invites => Set<Invite>();
    public DbSet<Progress> Progress => Set<Progress>();
    public DbSet<Note> Notes => Set<Note>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<User>(e =>
        {
            e.HasIndex(x => x.Login).IsUnique();
            e.Property(x => x.Login).HasMaxLength(32);
        });
        b.Entity<Invite>(e =>
        {
            e.HasIndex(x => x.CodeHash).IsUnique();
        });
        b.Entity<Progress>(e =>
        {
            e.HasKey(x => new { x.UserId, x.TopicSlug });
            e.Property(x => x.TopicSlug).HasMaxLength(300);
            e.HasIndex(x => new { x.UserId, x.Status });
        });
        b.Entity<Note>(e =>
        {
            e.Property(x => x.TopicSlug).HasMaxLength(300);
            e.Property(x => x.TopicTitle).HasMaxLength(300);
            e.Property(x => x.Body).HasMaxLength(20000);
            e.HasIndex(x => new { x.UserId, x.UpdatedAt });
            e.HasIndex(x => new { x.UserId, x.TopicSlug });
        });
    }
}
