from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, F, FloatField, ExpressionWrapper
from django.contrib.auth.models import User
from .models import TeamUpProfile, Team, TeamInvitation, Skill, TeamChat, TeamMessage
from .forms import TeamUpProfileForm, TeamCreationForm, TeamInvitationForm
from django.http import JsonResponse
from django.core.serializers import serialize
from django.utils import timezone
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from bs4 import BeautifulSoup

@ensure_csrf_cookie
@login_required
def dashboard(request):
    profile = request.user.teamup_profile
    teams = request.user.teams.all()
    created_teams = request.user.created_teams.all()
    pending_invitations = request.user.received_invitations.filter(status='pending')
    user_skills = profile.skills.all()
    user_interests = profile.interests.all()
    
    # Get recommended users excluding those already invited to any team by this user
    invited_user_ids = TeamInvitation.objects.filter(
        from_user=request.user, 
        status='pending'
    ).values_list('to_user_id', flat=True)
    
    recommended_users = TeamUpProfile.objects.filter(
        Q(skills__in=user_interests) | Q(interests__in=user_skills)
    ).exclude(user=request.user).exclude(user_id__in=invited_user_ids).distinct()
    
    # Sent invitations for all teams by this user
    sent_invitations = TeamInvitation.objects.filter(from_user=request.user, status='pending')
    
    context = {
        'profile': profile,
        'teams': teams,
        'created_teams': created_teams,
        'pending_invitations': pending_invitations,
        'recommended_users': recommended_users,
        'sent_invitations': sent_invitations,
    }
    
    if request.GET.get('ajax') == '1':
        html = render_to_string('teamup/dashboard.html', context, request=request)
        soup = BeautifulSoup(html, 'html.parser')
        received = soup.find(id='received-invitations')
        return JsonResponse({'html': str(received)})
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
    # Add recommended users and invite logic for consistency
    profile = request.user.teamup_profile
    teams = request.user.teams.all()
    user_skills = profile.skills.all()
    user_interests = profile.interests.all()
    recommended_users = TeamUpProfile.objects.filter(
        Q(skills__in=user_interests) | Q(interests__in=user_skills)
    ).exclude(user=request.user).distinct()
    sent_invites = TeamInvitation.objects.filter(from_user=request.user, status='pending')
    sent_invite_keys = set(f"{invite.to_user_id},{invite.team_id}" for invite in sent_invites)
    context = {
        'form': form,
        'recommended_users': recommended_users,
        'teams': teams,
        'sent_invite_keys': sent_invite_keys,
    }
    return render(request, 'teamup/profile_setup.html', context)

@login_required
def team_list(request):
    user_skills = request.user.teamup_profile.skills.all()
    user_skill_ids = list(user_skills.values_list('id', flat=True))

    # Annotate each team with the number of required skills and the number of matching skills
    teams = Team.objects.filter(status='open').annotate(
        required_skills_count=Count('required_skills', distinct=True),
        matching_skills_count=Count('required_skills', filter=Q(required_skills__in=user_skill_ids), distinct=True)
    ).annotate(
        skill_match_ratio=ExpressionWrapper(
            F('matching_skills_count') * 1.0 / F('required_skills_count'),
            output_field=FloatField()
        )
    ).filter(skill_match_ratio__gte=0.5)

    # Filter by skills if specified (optional, keeps UI filter working)
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
    # Only pending invitations for this team
    pending_invitations = team.invitations.filter(status='pending')
    # Chat context
    chat = None
    messages_qs = None
    if is_member:
        from .models import TeamChat, TeamMessage
        chat, _ = TeamChat.objects.get_or_create(team=team)
        chat.participants.set(team.members.all())
        messages_qs = chat.messages.select_related('sender').order_by('timestamp')
        # Handle message post
        if request.method == 'POST' and 'chat_message' in request.POST:
            content = request.POST.get('chat_message', '').strip()
            if content:
                TeamMessage.objects.create(chat=chat, sender=request.user, content=content)
            return redirect('teamup:team_detail', team_id=team_id)
    pending_invitation = TeamInvitation.objects.filter(
        team=team,
        to_user=request.user,
        status='pending'
    ).first()
    # Recommended users for this team (not already members or invited)
    user_skills = request.user.teamup_profile.skills.all()
    user_interests = request.user.teamup_profile.interests.all()
    recommended_users = TeamUpProfile.objects.filter(
        Q(skills__in=team.required_skills.all()) | Q(interests__in=team.required_skills.all())
    ).exclude(user__in=team.members.all()).exclude(user=request.user).distinct()
    sent_invite_keys = set(f"{invite.to_user_id},{invite.team_id}" for invite in team.invitations.filter(status='pending'))
    context = {
        'team': team,
        'is_member': is_member,
        'is_creator': is_creator,
        'pending_invitation': pending_invitation,
        'pending_invitations': pending_invitations,
        'chat': chat,
        'messages': messages_qs,
        'recommended_users': recommended_users,
        'sent_invite_keys': sent_invite_keys,
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
    try:
        invitation = TeamInvitation.objects.get(
            id=invitation_id,
            to_user=request.user,
            status='pending'
        )
    except TeamInvitation.DoesNotExist:
        messages.error(request, 'This invitation is no longer available or has already been handled.')
        return redirect('teamup:dashboard')
        
    action = request.POST.get('action')
    if action == 'accept':
        invitation.status = 'accepted'
        invitation.team.members.add(request.user)
        # Ensure chat exists and add user to chat participants
        chat, created = TeamChat.objects.get_or_create(team=invitation.team)
        chat.participants.set(invitation.team.members.all())
        messages.success(request, f'You have joined {invitation.team.title}!')
    elif action == 'decline':
        invitation.status = 'declined'
        messages.info(request, 'Invitation declined.')
    
    invitation.save()
    return redirect('teamup:dashboard')

@login_required
def send_unified_invitation(request):
    """Unified invitation system with team dropdown"""
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        user_id = request.POST.get('user_id')
        
        print(f"DEBUG: Received team_id={team_id}, user_id={user_id}")  # Debug log
        
        try:
            team = get_object_or_404(Team, id=team_id)
            to_user = get_object_or_404(User, id=user_id)
            
            # Check if user is a member of the team
            if request.user not in team.members.all():
                return JsonResponse({
                    'success': False, 
                    'error': 'You must be a team member to invite others.'
                }, status=403)
            
            # Check if user is already a member
            if to_user in team.members.all():
                return JsonResponse({
                    'success': False,
                    'error': 'User is already a member of this team.'
                }, status=400)
            
            # Use get_or_create to prevent duplicates
            invitation, created = TeamInvitation.objects.get_or_create(
                team=team,
                to_user=to_user,
                defaults={
                    'from_user': request.user,
                    'status': 'pending'
                }
            )
            
            if created:
                return JsonResponse({
                    'success': True,
                    'message': f'Invitation sent to {to_user.username} for {team.title}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invitation already exists for this user and team.'
                }, status=400)
                
        except Exception as e:
            print(f"DEBUG: Error sending invitation: {e}")  # Debug log
            return JsonResponse({
                'success': False,
                'error': 'An error occurred while sending the invitation.'
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@login_required
def cancel_invitation(request, invitation_id):
    """Cancel a sent invitation"""
    invitation = get_object_or_404(TeamInvitation, id=invitation_id, from_user=request.user, status='pending')
    invitation.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Invitation cancelled successfully.')
    return redirect('teamup:dashboard')

@login_required
def invite_user_from_dashboard(request):
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        user_id = request.POST.get('user_id')
        team = get_object_or_404(Team, id=team_id)
        to_user = get_object_or_404(User, id=user_id)
        if request.user not in team.members.all():
            return JsonResponse({'success': False, 'error': 'You must be a team member to invite.'}, status=403)
        # Only block if a pending invite exists
        if TeamInvitation.objects.filter(team=team, to_user=to_user, status='pending').exists():
            return JsonResponse({'success': False, 'error': 'Invitation already sent.'}, status=400)
        TeamInvitation.objects.create(team=team, from_user=request.user, to_user=to_user, status='pending')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)

@login_required
def team_chat(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user not in team.members.all():
        messages.error(request, 'You must be a team member to access the chat.')
        return redirect('teamup:team_detail', team_id=team_id)
    # Ensure chat exists
    chat, created = TeamChat.objects.get_or_create(team=team)
    chat.participants.set(team.members.all())
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            TeamMessage.objects.create(chat=chat, sender=request.user, content=content, timestamp=timezone.now())
        return redirect('teamup:team_chat', team_id=team_id)
    messages_qs = chat.messages.select_related('sender').order_by('timestamp')
    context = {
        'team': team,
        'chat': chat,
        'messages': messages_qs,
    }
    return render(request, 'teamup/team_chat.html', context)

@login_required
def team_chat_messages(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    if request.user not in team.members.all():
        return JsonResponse({'error': 'Not authorized'}, status=403)
    chat = getattr(team, 'chat', None)
    if not chat:
        return JsonResponse({'messages': []})
    messages = chat.messages.select_related('sender').order_by('timestamp')
    data = [
        {
            'sender': m.sender.username,
            'avatar': m.sender.teamup_profile.github_profile if hasattr(m.sender, 'teamup_profile') and m.sender.teamup_profile.github_profile else '',
            'timestamp': m.timestamp.strftime('%b %d, %H:%M'),
            'content': m.content,
        }
        for m in messages
    ]
    return JsonResponse({'messages': data})

@login_required
def send_team_invite(request):
    if request.method == "POST":
        team_id = request.POST.get('team_id')
        user_id = request.POST.get('user_id')
        team = Team.objects.get(id=team_id)
        receiver = User.objects.get(id=user_id)
        existing = TeamInvitation.objects.filter(team=team, receiver=receiver).order_by('-created_at').first()
        if existing and existing.status in ['pending', 'accepted']:
            return JsonResponse({'success': False, 'error': 'Already invited.'})
        TeamInvitation.objects.create(sender=request.user, receiver=receiver, team=team)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})

@login_required
def cancel_invite(request, invite_id):
    invite = get_object_or_404(TeamInvitation, id=invite_id, from_user=request.user)
    invite.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('teamup:dashboard')
