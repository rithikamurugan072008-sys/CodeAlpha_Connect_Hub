import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils.timesince import timesince
from django.conf import settings

from .models import Profile, Post, Like, Comment, Follow, Bookmark, Notification
from .forms import UserRegistrationForm, ProfileEditForm, PostForm


def get_suggested_users(current_user, limit=5):
    """Return users that the current user is not following yet."""
    if not current_user.is_authenticated:
        return User.objects.exclude(is_superuser=True).order_by('-date_joined')[:limit]
    
    following_ids = current_user.following_relations.values_list('following_id', flat=True)
    return User.objects.exclude(id=current_user.id).exclude(id__in=following_ids).exclude(is_superuser=True).order_by('?')[:limit]


def feed_view(request):
    """Main feed displaying posts (For You vs Following)."""
    tab = request.GET.get('tab', 'for-you')
    
    if tab == 'following' and request.user.is_authenticated:
        following_ids = request.user.following_relations.values_list('following_id', flat=True)
        # Show posts from people user follows + user's own posts
        posts = Post.objects.filter(Q(author_id__in=following_ids) | Q(author=request.user)).select_related('author', 'author__profile').prefetch_related('likes', 'comments')
    else:
        tab = 'for-you'
        posts = Post.objects.all().select_related('author', 'author__profile').prefetch_related('likes', 'comments')
    
    # Search filtering if search query provided
    q = request.GET.get('q', '').strip()
    if q:
        posts = posts.filter(Q(content__icontains=q) | Q(author__username__icontains=q))

    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    suggested_users = get_suggested_users(request.user)
    
    # Trending hashtags simulation
    trending_tags = [
        {"tag": "#WebDevelopment", "posts_count": "14.2K"},
        {"tag": "#DjangoPython", "posts_count": "9.8K"},
        {"tag": "#TechInnovation", "posts_count": "8.1K"},
        {"tag": "#DesignSystem", "posts_count": "6.4K"},
        {"tag": "#FullStack", "posts_count": "5.0K"},
    ]

    context = {
        'page_obj': page_obj,
        'tab': tab,
        'search_query': q,
        'suggested_users': suggested_users,
        'trending_tags': trending_tags,
        'post_form': PostForm() if request.user.is_authenticated else None,
    }
    return render(request, 'network/feed.html', context)


def explore_view(request):
    """Explore page with trending posts and discovering creators."""
    q = request.GET.get('q', '').strip()
    matching_users = []
    
    if q:
        posts = Post.objects.filter(Q(content__icontains=q) | Q(author__username__icontains=q)).select_related('author', 'author__profile')
        matching_users = User.objects.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))[:8]
    else:
        # Explore shows all posts, ordered by likes count / recency
        posts = Post.objects.annotate(likes_num=Count('likes')).order_by('-likes_num', '-created_at').select_related('author', 'author__profile')
        matching_users = User.objects.exclude(is_superuser=True).order_by('?')[:6]

    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': q,
        'matching_users': matching_users,
        'suggested_users': get_suggested_users(request.user, limit=5),
    }
    return render(request, 'network/explore.html', context)


@login_required
def bookmarks_view(request):
    """User's bookmarked / saved posts."""
    bookmarked_post_ids = request.user.bookmarks.values_list('post_id', flat=True)
    posts = Post.objects.filter(id__in=bookmarked_post_ids).select_related('author', 'author__profile')
    
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'suggested_users': get_suggested_users(request.user),
    }
    return render(request, 'network/bookmarks.html', context)


def profile_view(request, username):
    """User profile page showing details, stats, posts, and liked posts."""
    profile_user = get_object_or_404(User.objects.select_related('profile'), username__iexact=username)
    tab = request.GET.get('tab', 'posts')

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    if tab == 'likes':
        liked_post_ids = profile_user.likes.values_list('post_id', flat=True)
        posts = Post.objects.filter(id__in=liked_post_ids).select_related('author', 'author__profile')
    elif tab == 'media':
        posts = profile_user.posts.exclude(image='').exclude(image__isnull=True).select_related('author', 'author__profile')
    else:
        tab = 'posts'
        posts = profile_user.posts.all().select_related('author', 'author__profile')

    paginator = Paginator(posts, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': profile_user,
        'profile': profile_user.profile,
        'is_following': is_following,
        'tab': tab,
        'page_obj': page_obj,
        'edit_form': ProfileEditForm(instance=profile_user.profile) if request.user == profile_user else None,
        'suggested_users': get_suggested_users(request.user),
    }
    return render(request, 'network/profile.html', context)


@login_required
@require_POST
def edit_profile_view(request):
    """Handle editing user profile information."""
    profile = request.user.profile
    form = ProfileEditForm(request.POST, request.FILES, instance=profile)
    
    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    
    if form.is_valid():
        form.save()
        if first_name is not None:
            request.user.first_name = first_name
        if last_name is not None:
            request.user.last_name = last_name
        request.user.save()
        return redirect('profile', username=request.user.username)
    
    return redirect('profile', username=request.user.username)


def post_detail_view(request, post_id):
    """Detailed view for a single post with all its comments."""
    post = get_object_or_404(Post.objects.select_related('author', 'author__profile'), id=post_id)
    comments = post.comments.select_related('author', 'author__profile').all()
    
    is_liked = post.is_liked_by(request.user)
    is_bookmarked = post.is_bookmarked_by(request.user)

    context = {
        'post': post,
        'comments': comments,
        'is_liked': is_liked,
        'is_bookmarked': is_bookmarked,
        'suggested_users': get_suggested_users(request.user),
    }
    return render(request, 'network/post_detail.html', context)


# ============================================================
# API ENDPOINTS (Interactive JSON responses for JS frontend)
# ============================================================

@login_required
@require_POST
def create_post_api(request):
    """API endpoint to create a new post with text and optional image."""
    content = request.POST.get('content', '').strip()
    image = request.FILES.get('image')

    if not content and not image:
        return JsonResponse({'status': 'error', 'message': 'Post content or image is required.'}, status=400)

    post = Post.objects.create(
        author=request.user,
        content=content,
        image=image
    )

    return JsonResponse({
        'status': 'success',
        'message': 'Post published successfully!',
        'post': {
            'id': post.id,
            'content': post.content,
            'image_url': post.image.url if post.image else None,
            'created_at': 'just now',
            'author_username': post.author.username,
            'author_name': post.author.get_full_name() or post.author.username,
            'author_avatar': post.author.profile.get_avatar_url(),
            'likes_count': 0,
            'comments_count': 0,
            'is_liked': False,
            'is_bookmarked': False,
        }
    })


@login_required
@require_POST
def delete_post_api(request, post_id):
    """API endpoint to delete a post if caller is author."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user and not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)
    
    post.delete()
    return JsonResponse({'status': 'success', 'message': 'Post deleted.'})


@require_POST
def toggle_like_api(request, post_id):
    """API endpoint to toggle like on a post."""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to like posts.'}, status=401)

    post = get_object_or_404(Post, id=post_id)
    like = Like.objects.filter(user=request.user, post=post).first()

    if like:
        like.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True
        # Create notification if liking someone else's post
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post
            )

    return JsonResponse({
        'status': 'success',
        'liked': liked,
        'likes_count': post.likes_count()
    })


@login_required
@require_POST
def toggle_bookmark_api(request, post_id):
    """API endpoint to toggle bookmark on a post."""
    post = get_object_or_404(Post, id=post_id)
    bookmark = Bookmark.objects.filter(user=request.user, post=post).first()

    if bookmark:
        bookmark.delete()
        bookmarked = False
    else:
        Bookmark.objects.create(user=request.user, post=post)
        bookmarked = True

    return JsonResponse({
        'status': 'success',
        'bookmarked': bookmarked
    })


@login_required
@require_POST
def add_comment_api(request, post_id):
    """API endpoint to add a comment to a post."""
    post = get_object_or_404(Post, id=post_id)
    
    # Can be form-encoded or JSON
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
        except json.JSONDecodeError:
            content = ''
    else:
        content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'status': 'error', 'message': 'Comment cannot be empty.'}, status=400)

    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content
    )

    # Create notification if commenting on someone else's post
    if post.author != request.user:
        Notification.objects.create(
            recipient=post.author,
            sender=request.user,
            notification_type='comment',
            post=post
        )

    return JsonResponse({
        'status': 'success',
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'created_at': 'just now',
            'author_username': comment.author.username,
            'author_name': comment.author.get_full_name() or comment.author.username,
            'author_avatar': comment.author.profile.get_avatar_url(),
            'is_author': True
        },
        'comments_count': post.comments_count()
    })


@login_required
@require_POST
def delete_comment_api(request, comment_id):
    """API endpoint to delete a comment."""
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user and comment.post.author != request.user and not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)
    
    post = comment.post
    comment.delete()
    return JsonResponse({
        'status': 'success',
        'message': 'Comment deleted.',
        'comments_count': post.comments_count()
    })


@login_required
@require_POST
def toggle_follow_api(request, username):
    """API endpoint to follow or unfollow another user."""
    target_user = get_object_or_404(User, username__iexact=username)
    
    if target_user == request.user:
        return JsonResponse({'status': 'error', 'message': 'You cannot follow yourself.'}, status=400)

    follow = Follow.objects.filter(follower=request.user, following=target_user).first()
    if follow:
        follow.delete()
        is_following = False
    else:
        Follow.objects.create(follower=request.user, following=target_user)
        is_following = True
        # Create notification
        Notification.objects.create(
            recipient=target_user,
            sender=request.user,
            notification_type='follow'
        )

    return JsonResponse({
        'status': 'success',
        'is_following': is_following,
        'followers_count': target_user.follower_relations.count()
    })


def followers_list_api(request, username):
    """Return list of followers for a user as JSON."""
    target_user = get_object_or_404(User, username__iexact=username)
    followers = Follow.objects.filter(following=target_user).select_related('follower', 'follower__profile')
    
    data = []
    for f in followers:
        u = f.follower
        is_following = False
        if request.user.is_authenticated and request.user != u:
            is_following = Follow.objects.filter(follower=request.user, following=u).exists()
            
        data.append({
            'username': u.username,
            'name': u.get_full_name() or u.username,
            'avatar': u.profile.get_avatar_url(),
            'bio': u.profile.bio[:80] if u.profile.bio else '',
            'is_following': is_following,
            'is_self': request.user == u
        })
    return JsonResponse({'status': 'success', 'users': data})


def following_list_api(request, username):
    """Return list of accounts followed by user as JSON."""
    target_user = get_object_or_404(User, username__iexact=username)
    following = Follow.objects.filter(follower=target_user).select_related('following', 'following__profile')
    
    data = []
    for f in following:
        u = f.following
        is_following = False
        if request.user.is_authenticated and request.user != u:
            is_following = Follow.objects.filter(follower=request.user, following=u).exists()
            
        data.append({
            'username': u.username,
            'name': u.get_full_name() or u.username,
            'avatar': u.profile.get_avatar_url(),
            'bio': u.profile.bio[:80] if u.profile.bio else '',
            'is_following': is_following,
            'is_self': request.user == u
        })
    return JsonResponse({'status': 'success', 'users': data})


def search_api(request):
    """Live search endpoint for users and posts."""
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'users': [], 'posts': []})

    users = User.objects.filter(
        Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
    ).exclude(is_superuser=True)[:5]

    posts = Post.objects.filter(content__icontains=q)[:5]

    user_data = [{
        'username': u.username,
        'name': u.get_full_name() or u.username,
        'avatar': u.profile.get_avatar_url()
    } for u in users]

    post_data = [{
        'id': p.id,
        'content': p.content[:100] + ('...' if len(p.content) > 100 else ''),
        'author_username': p.author.username
    } for p in posts]

    return JsonResponse({'users': user_data, 'posts': post_data})


@login_required
def notifications_view(request):
    """User notifications list."""
    notifications = request.user.notifications.select_related('sender', 'sender__profile', 'post').all()[:30]
    # Mark as read
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'network/notifications.html', {
        'notifications': notifications,
        'suggested_users': get_suggested_users(request.user)
    })


@login_required
@require_POST
def mark_notifications_read_api(request):
    """Mark all notifications as read."""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})


# ============================================================
# AUTHENTICATION VIEWS & DEMO QUICK-LOGIN
# ============================================================

def register_view(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('feed')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Save bio
            bio = form.cleaned_data.get('bio', '')
            if bio:
                user.profile.bio = bio
                user.profile.save()
                
            login(request, user)
            return redirect('feed')
    else:
        form = UserRegistrationForm()

    return render(request, 'network/register.html', {'form': form})


def login_view(request):
    """User login page with username or email authentication."""
    if request.user.is_authenticated:
        return redirect('feed')

    error_message = None
    if request.method == 'POST':
        username_input = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '').strip()

        # 1. Try direct authentication (matches username)
        user = authenticate(request, username=username_input, password=password_input)

        # 2. If failed, attempt lookup by email
        if user is None:
            try:
                user_by_email = User.objects.filter(email__iexact=username_input).first()
                if user_by_email:
                    user = authenticate(request, username=user_by_email.username, password=password_input)
            except Exception:
                user = None

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next') or 'feed'
            return redirect(next_url)
        else:
            error_message = 'Invalid username/email or password. Please try again.'

    # Available demo users for one-click instant testing
    demo_users = User.objects.exclude(is_superuser=True)[:5]

    return render(request, 'network/login.html', {
        'error_message': error_message,
        'demo_users': demo_users
    })


def quick_login_api(request, username):
    """Quick login helper for fast testing between different users."""
    user = get_object_or_404(User, username__iexact=username)
    login(request, user)
    return redirect('feed')


def logout_view(request):
    """Log out current user."""
    logout(request)
    return redirect('login')
