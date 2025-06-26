from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import UserDashboard, Guild, Post, Comment, Organiser, Sponsor, Sponsorship, Event, ChatRoom, Message
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponseForbidden
from collections import defaultdict
from .forms import EventForm
from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

def landing(request):
    return render(request, 'skilledguild/landing.html')

def login_register(request):
    login_error = None
    register_error = None
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login':
            username = request.POST.get('login_username')
            password = request.POST.get('login_password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('guilds')
            else:
                login_error = 'Invalid username or password.'
        elif action == 'register':
            username = request.POST.get('register_username')
            email = request.POST.get('register_email')
            password1 = request.POST.get('register_password1')
            password2 = request.POST.get('register_password2')
            if password1 != password2:
                register_error = 'Passwords do not match.'
            elif User.objects.filter(username=username).exists():
                register_error = 'Username already exists.'
            elif User.objects.filter(email=email).exists():
                register_error = 'Email already registered.'
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                auth_login(request, user)
                return redirect('guilds')
    return render(request, 'skilledguild/login_register.html', {
        'login_error': login_error,
        'register_error': register_error
    })

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login_register')
    dashboard_obj, created = UserDashboard.objects.get_or_create(user=request.user)
    dashboard_obj.visit_count += 1
    dashboard_obj.last_login = timezone.now()
    dashboard_obj.save()
    context = {
        'user': request.user,
        'visit_count': dashboard_obj.visit_count,
        'last_login': dashboard_obj.last_login,
    }
    return render(request, 'skilledguild/dashboard.html', context)

@login_required
def guilds(request):
    guild_list = Guild.objects.all()
    user_guild_ids = set()
    if request.user.is_authenticated:
        user_guild_ids = set(request.user.guilds.values_list('id', flat=True))
    return render(request, 'skilledguild/guilds.html', {
        'guilds': guild_list,
        'user_guild_ids': user_guild_ids,
    })

@login_required
def toggle_guild_membership(request, guild_id):
    guild = get_object_or_404(Guild, id=guild_id)
    if request.method == 'POST':
        if request.user in guild.members.all():
            guild.members.remove(request.user)
            joined = False
        else:
            guild.members.add(request.user)
            joined = True
        # If AJAX, return JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'joined': joined})
        # Otherwise, redirect back
        next_url = request.META.get('HTTP_REFERER') or 'guilds'
        return redirect(next_url)
    return HttpResponseForbidden()

@login_required
def guild_detail(request, guild_id):
    guild = get_object_or_404(Guild, id=guild_id)
    is_member = request.user in guild.members.all()
    posts = guild.posts.order_by('-timestamp')
    if request.method == 'POST' and is_member:
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Post.objects.create(title=title, content=content, author=request.user, guild=guild)
            return redirect('guild_detail', guild_id=guild.id)
    return render(request, 'skilledguild/guild_detail.html', {
        'guild': guild,
        'is_member': is_member,
        'posts': posts,
    })

@login_required
def post_detail(request, guild_id, post_id):
    guild = get_object_or_404(Guild, id=guild_id)
    post = get_object_or_404(Post, id=post_id, guild=guild)
    is_member = request.user in guild.members.all()
    comments = post.comments.select_related('author').order_by('timestamp')
    if request.method == 'POST' and is_member:
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
            return redirect('post_detail', guild_id=guild.id, post_id=post.id)
    return render(request, 'skilledguild/post_detail.html', {
        'guild': guild,
        'post': post,
        'comments': comments,
        'is_member': is_member,
    })

@login_required
def create_post(request, guild_id):
    guild = get_object_or_404(Guild, id=guild_id)
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            Post.objects.create(
                title=title,
                content=content,
                author=request.user,
                guild=guild
            )
            return redirect('guild_detail', guild_id=guild.id)
    return render(request, 'skilledguild/create_post.html', {'guild': guild})

@login_required
def sponsorverse(request):
    organisers = Organiser.objects.all()
    sponsors = Sponsor.objects.all()
    organiser_groups = defaultdict(list)
    for o in organisers:
        organiser_groups[o.category].append(o)
    sponsor_groups = defaultdict(list)
    for s in sponsors:
        sponsor_groups[s.type].append(s)

    # Event creation logic
    if request.method == 'POST' and 'add_event' in request.POST:
        form = EventForm(request.POST)
        print('Event form POST data:', request.POST)  # Debug
        if form.is_valid():
            print('Event form is valid!')  # Debug
            event = form.save(commit=False)
            # Remove organiser requirement
            try:
                organiser = request.user.organiser_profile
            except Exception:
                organiser = None
            event.organiser = organiser  # organiser may be None
            event.save()
            print('Event saved! ID:', event.id)  # Debug
            messages.success(request, 'Event added successfully!')
            return redirect('sponsorverse')
        else:
            print('Event form is NOT valid:', form.errors)  # Debug
    else:
        form = EventForm()

    events = Event.objects.all().order_by('-created_at')

    return render(request, 'skilledguild/sponsorverse.html', {
        'organiser_groups': dict(organiser_groups),
        'sponsor_groups': dict(sponsor_groups),
        'event_form': form,
        'events': events,
    })

@login_required
@require_POST
def sponsor_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    amount = request.POST.get('amount')
    message = request.POST.get('message', '')
    contact_info = request.POST.get('contact_info', '')
    if not amount or not contact_info:
        messages.error(request, 'Amount and contact info are required.')
        return redirect('sponsorverse')
    try:
        amount = float(amount)
    except ValueError:
        messages.error(request, 'Invalid amount.')
        return redirect('sponsorverse')
    sponsorship = Sponsorship.objects.create(
        event=event,
        investor=request.user,
        amount=amount,
        message=message,
        contact_info=contact_info
    )
    # Find or create chat room for this event, organiser, and sponsor
    organiser_user = event.organiser.user if event.organiser and event.organiser.user else None
    sponsor_user = request.user
    chatroom = ChatRoom.objects.filter(event=event, users=organiser_user).filter(users=sponsor_user).first() if organiser_user else None
    if not chatroom and organiser_user:
        chatroom = ChatRoom.objects.create(event=event)
        chatroom.users.add(organiser_user, sponsor_user)
        chatroom.save()
        Message.objects.create(
            chatroom=chatroom,
            sender=organiser_user,
            content=f"Welcome! This chat is for {sponsor_user.username} and {organiser_user.username} to discuss the sponsorship of '{event.name}'.",
        )
    messages.success(request, 'Sponsorship successful!')
    return redirect('sponsorverse')
