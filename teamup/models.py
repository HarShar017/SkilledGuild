from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class TeamUpProfile(models.Model):
    AVAILABILITY_CHOICES = [
        ('available', 'Available for Projects'),
        ('busy', 'Currently Busy'),
        ('open_to_discussion', 'Open to Discussion'),
        ('unavailable', 'Unavailable'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teamup_profile')
    bio = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, related_name='skilled_users')
    interests = models.ManyToManyField(Skill, related_name='interested_users')
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='available'
    )
    github_profile = models.URLField(blank=True)
    linkedin_profile = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s TeamUp Profile"

    @property
    def location(self):
        parts = [p for p in [self.city, self.state, self.country] if p]
        return ', '.join(parts)

class Team(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open for Members'),
        ('closed', 'Team Full'),
        ('completed', 'Project Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    members = models.ManyToManyField(User, related_name='teams')
    required_skills = models.ManyToManyField(Skill, related_name='required_by_teams')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    max_members = models.PositiveIntegerField(default=5)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def is_full(self):
        return self.members.count() >= self.max_members

class TeamInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='invitations')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invitations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"Invitation to {self.to_user.username} for {self.team.title}"

@receiver(post_save, sender=User)
def create_teamup_profile(sender, instance, created, **kwargs):
    if created:
        TeamUpProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_teamup_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'teamup_profile'):
        TeamUpProfile.objects.create(user=instance)
    instance.teamup_profile.save()
