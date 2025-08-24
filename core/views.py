from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

from .models import Post, Comment, Profile
from .forms import PostForm, CommentForm



# 🏠 Home View: Post & Comment Logic
@login_required
def home(request):
    comment_form = CommentForm()
    filter_option = request.GET.get('filter')

    if filter_option == 'following':
        followed_profiles = request.user.following.all()
        followed_users = User.objects.filter(profile__in=followed_profiles)
        posts = Post.objects.filter(user__in=followed_users)  # Only following users
    elif filter_option == 'mine':
        posts = Post.objects.filter(user=request.user)
    else:
        posts = Post.objects.all()

    posts = posts.order_by('-created_at')

    if request.method == 'POST' and 'submit_comment' in request.POST:
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('home')

    return render(request, 'home.html', {
        'comment_form': comment_form,
        'posts': posts,
    })





# 📝 Register
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# 🔐 Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            # Ensure Profile exists
            Profile.objects.get_or_create(user=user)

            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# 🚪 Logout
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# 👤 Profile View
from .forms import ProfileForm
@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    is_own_profile = request.user == profile_user

    if is_own_profile:
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('profile', username=username)
        else:
            form = ProfileForm(instance=profile)
    else:
        form = None  # Hide form if viewing others' profiles

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'form': form,
    })



# 🗑️ Delete Post

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
    return redirect('home')


# ❤️ Toggle Like
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('home')


# ➕➖ Toggle Follow
@login_required
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    profile = target_user.profile

    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
    else:
        profile.followers.add(request.user)

    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def followers_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = profile_user.profile.followers.all()
    return render(request, 'followers_list.html', {
        'title': f"{username}'s Followers",
        'users': followers
    })

@login_required
def following_list(request, username):
    profile_user = get_object_or_404(User, username=username)

    # Get Profile instances this user is following
    followed_profiles = profile_user.following.all()  # These are Profile objects

    # Get User instances from those Profiles
    followed_users = [profile.user for profile in followed_profiles if profile.user is not None]

    return render(request, 'followers_list.html', {
        'title': f"{username} is Following",
        'users': followed_users
    })

from django.db.models import Q
from .models import User, Post

@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    user_results = []
    post_results = []
    if query:
        user_results = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        post_results = Post.objects.filter(
            Q(content__icontains=query) |
            Q(user__username__icontains=query)
        )
    return render(request, 'search_results.html', {
        'query': query,
        'user_results': user_results,
        'post_results': post_results,
    })


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')  # or redirect to post detail/profile page
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})

@login_required
def toggle_save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.saved_by.all():
        post.saved_by.remove(request.user)
    else:
        post.saved_by.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def saved_posts(request):
    posts = request.user.saved_posts.all().order_by('-created_at')
    return render(request, 'saved_posts.html', {'posts': posts})