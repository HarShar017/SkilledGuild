from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('auth/', views.login_register, name='login_register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='login_register', http_method_names=['post', 'get']), name='logout'),
    path('guilds/', views.guilds, name='guilds'),
    path('guilds/<int:guild_id>/toggle/', views.toggle_guild_membership, name='toggle_guild_membership'),
    path('guilds/<int:guild_id>/', views.guild_detail, name='guild_detail'),
    path('guilds/<int:guild_id>/post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('guilds/<int:guild_id>/create/', views.create_post, name='create_post'),
    path('sponsorverse/', views.sponsorverse, name='sponsorverse'),
    path('sponsorverse/sponsor/<int:event_id>/', views.sponsor_event, name='sponsor_event'),
]
