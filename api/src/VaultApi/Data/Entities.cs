namespace VaultApi.Data;

public enum Role { User = 0, Admin = 1 }

public enum TopicStatus { Todo = 0, InProgress = 1, Done = 2 }

public class User
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Login { get; set; } = "";
    public string PasswordHash { get; set; } = "";
    public Role Role { get; set; }
    public bool IsBlocked { get; set; }
    // меняется при смене пароля: старые cookie-сессии перестают действовать
    public Guid SecurityStamp { get; set; } = Guid.NewGuid();
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class Invite
{
    public Guid Id { get; set; } = Guid.NewGuid();
    // в базе хранится только хэш кода
    public string CodeHash { get; set; } = "";
    public Guid CreatedById { get; set; }
    public Guid? UsedById { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime ExpiresAt { get; set; }
}

// Отметка пользователя о теме. Тема идентифицируется slug (путь страницы на сайте).
public class Progress
{
    public Guid UserId { get; set; }
    public string TopicSlug { get; set; } = "";
    public TopicStatus Status { get; set; }
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? ReviewedAt { get; set; }
    public DateTime? NextReviewAt { get; set; }
}

public class Note
{
    public Guid Id { get; set; } = Guid.NewGuid();
    public Guid UserId { get; set; }
    public string TopicSlug { get; set; } = "";
    // название темы сохраняем в заметке, чтобы общий список не зависел от содержимого сайта
    public string TopicTitle { get; set; } = "";
    public string Body { get; set; } = "";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}
