from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserDashboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard')
    visit_count = models.PositiveIntegerField(default=0)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Dashboard for {self.user.username}"


class Guild(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon_url = models.URLField(blank=True, null=True)
    theme_color = models.CharField(max_length=16, blank=True, null=True, help_text='Hex color for card accent')
    members = models.ManyToManyField(User, related_name='guilds', blank=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='posts')
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True, help_text='Comma-separated tags')
    
    def __str__(self):
        return f"{self.title} ({self.guild.name})"
    
    def comment_count(self):
        return self.comments.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
