from django.shortcuts import render

def quests_orgg_dashboard(request):
    return render(request, 'quests_orgg/quests_orgg_dashboard.html')
