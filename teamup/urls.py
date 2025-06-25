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
]