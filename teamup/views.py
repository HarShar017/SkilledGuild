from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from .models import TeamUpProfile, Team, TeamInvitation, Skill
from .forms import TeamUpProfileForm, TeamCreationForm, TeamInvitationForm

@login_required
def dashboard(request):
    profile = request.user.teamup_profile
    teams = request.user.teams.all()
    created_teams = request.user.created_teams.all()
    pending_invitations = request.user.received_invitations.filter(status='pending')
    
    # Get recommended users based on shared skills and interests
    user_skills = profile.skills.all()
    user_interests = profile.interests.all()
    
    recommended_users = TeamUpProfile.objects.filter(
        Q(skills__in=user_interests) | Q(interests__in=user_skills)
    ).exclude(user=request.user).distinct()
    
    context = {
        'profile': profile,
        'teams': teams,
        'created_teams': created_teams,
        'pending_invitations': pending_invitations,
        'recommended_users': recommended_users,
    }
    return render(request, 'teamup/dashboard.html', context)

@login_required
def profile_setup(request):
    if request.method == 'POST':
        form = TeamUpProfileForm(request.POST, instance=request.user.teamup_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your TeamUp profile has been updated!')
            return redirect('teamup:dashboard')
    else:
        form = TeamUpProfileForm(instance=request.user.teamup_profile)
    
    context = {'form': form}
    return render(request, 'teamup/profile_setup.html', context)

@login_required
def team_list(request):
    teams = Team.objects.filter(status='open')
    user_skills = request.user.teamup_profile.skills.all()
    
    # Filter by skills if specified
    skill_filter = request.GET.getlist('skills')
    if skill_filter:
        teams = teams.filter(required_skills__id__in=skill_filter).distinct()
    
    context = {
        'teams': teams,
        'user_skills': user_skills,
        'all_skills': Skill.objects.all(),
    }
    return render(request, 'teamup/team_list.html', context)

@login_required
def create_team(request):
    if request.method == 'POST':
        form = TeamCreationForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.creator = request.user
            team.save()
            form.save_m2m()  # Save many-to-many relationships
            team.members.add(request.user)  # Add creator as a member
            messages.success(request, 'Team created successfully!')
            return redirect('teamup:team_detail', team_id=team.id)
    else:
        form = TeamCreationForm()
    
    context = {'form': form}
    return render(request, 'teamup/create_team.html', context)

@login_required
def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    is_member = request.user in team.members.all()
    is_creator = team.creator == request.user
    pending_invitation = TeamInvitation.objects.filter(
        team=team,
        to_user=request.user,
        status='pending'
    ).first()
    
    context = {
        'team': team,
        'is_member': is_member,
        'is_creator': is_creator,
        'pending_invitation': pending_invitation,
    }
    return render(request, 'teamup/team_detail.html', context)

@login_required
def send_invitation(request, team_id, user_id):
    if request.method == 'POST':
        team = get_object_or_404(Team, id=team_id)
        to_user = get_object_or_404(User, id=user_id)
        
        if request.user not in team.members.all():
            messages.error(request, 'You must be a team member to send invitations.')
            return redirect('teamup:team_detail', team_id=team_id)
        
        invitation = TeamInvitation.objects.create(
            team=team,
            from_user=request.user,
            to_user=to_user,
            message=request.POST.get('message', '')
        )
        messages.success(request, f'Invitation sent to {to_user.username}!')
    
    return redirect('teamup:team_detail', team_id=team_id)

@login_required
def handle_invitation(request, invitation_id):
    invitation = get_object_or_404(
        TeamInvitation,
        id=invitation_id,
        to_user=request.user,
        status='pending'
    )
    
    action = request.POST.get('action')
    if action == 'accept':
        invitation.status = 'accepted'
        invitation.team.members.add(request.user)
        messages.success(request, f'You have joined {invitation.team.title}!')
    elif action == 'decline':
        invitation.status = 'declined'
        messages.info(request, 'Invitation declined.')
    
    invitation.save()
    return redirect('teamup:dashboard')
