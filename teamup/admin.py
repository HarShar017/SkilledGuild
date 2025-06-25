from django.contrib import admin
from .models import Skill, TeamUpProfile, Team, TeamInvitation

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'category')
    list_filter = ('category',)

@admin.register(TeamUpProfile)
class TeamUpProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'availability_status', 'location')
    list_filter = ('availability_status',)
    search_fields = ('user__username', 'bio', 'city', 'state', 'country')
    filter_horizontal = ('skills', 'interests')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'status', 'created_at', 'member_count')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'creator__username')
    filter_horizontal = ('members', 'required_skills')
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'

@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    list_display = ('team', 'from_user', 'to_user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('team__title', 'from_user__username', 'to_user__username')
