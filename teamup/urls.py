from django.urls import path
from . import views

app_name = 'teamup'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/setup/', views.profile_setup, name='profile_setup'),
    path('teams/', views.team_list, name='team_list'),
    path('teams/create/', views.create_team, name='create_team'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('teams/<int:team_id>/invite/<int:user_id>/', views.send_invitation, name='send_invitation'),
    path('invitations/<int:invitation_id>/handle/', views.handle_invitation, name='handle_invitation'),
    path('invite-user/', views.invite_user_from_dashboard, name='invite_user_from_dashboard'),
    path('send-invitation/', views.send_unified_invitation, name='send_unified_invitation'),
    path('invitations/<int:invitation_id>/cancel/', views.cancel_invitation, name='cancel_invitation'),
    path('teams/<int:team_id>/chat/', views.team_chat, name='team_chat'),
    path('teams/<int:team_id>/chat/messages/', views.team_chat_messages, name='team_chat_messages'),
    path('cancel-invite/<int:invite_id>/', views.cancel_invite, name='cancel_invite'),
]