from django.urls import path
from . import views

urlpatterns = [
    path('', views.quests_orgg_dashboard, name='quests_orgg'),
]