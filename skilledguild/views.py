from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import UserDashboard, Guild, Post, Comment
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponseForbidden

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
    if request.method == 'POST':
        guild = get_object_or_404(Guild, id=guild_id)
        if request.user in guild.members.all():
            guild.members.remove(request.user)
            joined = False
        else:
            guild.members.add(request.user)
            joined = True
        return JsonResponse({'joined': joined})
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
