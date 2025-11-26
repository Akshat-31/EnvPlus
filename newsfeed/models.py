from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        abstract = True


class User(AbstractUser):
    SECURITY_QUESTIONS = [
        ("pet", "What is your first pet's name?"),
        ("school", "What was your high school name?"),
        ("city", "In what city were you born?"),
        ("nickname", "What was your childhood nickname?"),
    ]

    bio = models.TextField(max_length=500, blank=True)
    is_admin = models.BooleanField(default=False)
    is_author = models.BooleanField(default=False)
    member_since = models.DateTimeField(auto_now_add=True)
    last_login_count = models.IntegerField(default=0)
    security_question = models.CharField(max_length=100, choices=SECURITY_QUESTIONS, null=True, blank=True)
    security_answer_hash = models.CharField(max_length=255, null=True, blank=True)

    def set_security_answer(self, answer):
        self.security_answer_hash = make_password(answer.lower().strip())

    def check_security_answer(self, answer):
        return check_password(answer.lower().strip(), self.security_answer_hash)
    
    def __str__(self):
        return self.username
    
    def can_manage_articles(self):
        return self.is_admin or self.is_staff or self.is_author


class Category(TimestampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Article(TimestampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    image = models.ImageField(upload_to='articles/', null=True, blank=True)
    read_time = models.IntegerField()
    views = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    
    def total_likes(self):
        return self.likes.count()
    
    def total_comments(self):
        return self.comments.count()
    
    def __str__(self):
        return self.title


class Like(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    
    class Meta:
        unique_together = ('user', 'article')
    
    def __str__(self):
        return f"{self.user.username} likes {self.article.title}"


class Comment(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"


class SavedArticle(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_articles')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='saved_by')
    
    def __str__(self):
        return f"{self.user.username} saved {self.article.title}"


class ReadHistory(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_history')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='readers')
    read_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} read {self.article.title}"


