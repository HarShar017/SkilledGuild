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

class Organiser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organiser_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='organiser_logos/')
    description = models.TextField()
    category = models.CharField(max_length=100, help_text='e.g., Club Chapter, Host Institute')
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Sponsor(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='sponsor_logos/')
    description = models.TextField()
    type = models.CharField(max_length=100, help_text='e.g., Title Sponsor, Outreach Partner')
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    organiser = models.ForeignKey(Organiser, on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    sponsorship_goals = models.TextField(help_text='Sponsorship goals or requirements')
    contact_info = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.organiser.name if self.organiser else 'No organiser'})"

class Sponsorship(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sponsorships')
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sponsorships')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    contact_info = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.investor.username} sponsored {self.event.name} for {self.amount}"

class ChatRoom(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='chatrooms')
    users = models.ManyToManyField(User, related_name='chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom for {self.event.name} ({', '.join([u.username for u in self.users.all()])})"

class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}..."
