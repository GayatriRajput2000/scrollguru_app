import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Content, Category, UserStreak, Story
from django.db import models  # ← Yeh missing tha bhai, isko add kiya!
from django.db.models import Q, F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from .models import Follow
from django.utils import timezone
# Group by user for better UI
from itertools import groupby
from operator import attrgetter

def get_or_create_streak(request):
    """
    Handles streaks seamlessly for both anonymous session users and logged-in accounts.
    """
    today = timezone.now().date()
    
    if request.user.is_authenticated:
        # User is logged in: Check DB model attributes directly
        user = request.user
        if user.created_at:
            # Check if user logged in today already or continuing streak
            # Using custom model simulation logic for streak intervals
            pass
        # Fallback tracking safely handled inside global session model for parity
    
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    streak, created = UserStreak.objects.get_or_create(session_key=session_key)
    
    if streak.last_login_date:
        days_diff = (today - streak.last_login_date).days
        if days_diff == 1:
            streak.current_streak += 1
        elif days_diff > 1:
            streak.current_streak = 1
    else:
        streak.current_streak = 1
    
    streak.last_login_date = today
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.save()
    
    # Sync safely with CustomUser database profile if logged in
    if request.user.is_authenticated:
        request.user.streak = streak.current_streak
        request.user.save(update_fields=['streak'])
        
    return streak




def home(request):
    category_slug = request.GET.get('category')
    lang = request.GET.get('lang')
    search = request.GET.get('search')
    
    contents = Content.objects.all()
    
    if category_slug: contents = contents.filter(category__slug=category_slug)
    if lang: contents = contents.filter(language=lang)
    if search: contents = contents.filter(title__icontains=search)
    
    return render(request, 'feed.html', {
        'contents': contents[:5], # Initial load limited for speed
        'categories': Category.objects.all(),
        'selected_category': category_slug,
        'selected_lang': lang
    })

def load_more(request):
    # Bug Fix: Direct HTML response for HTMX
    page = int(request.GET.get('page', 1))
    start = (page - 1) * 5
    contents = Content.objects.all()[start : start + 5]
    
    if not contents: return HttpResponse("") # Stop HTMX

    html = ""
    for c in contents:
        html += f'''
        <div class="video-slide" data-content-id="{c.id}">
            <video loop muted playsinline class="w-full h-full object-cover">
                <source src="{c.video_url}" type="video/mp4">
            </video>
            <div class="absolute bottom-0 p-6 text-white z-10 w-full bg-gradient-to-t from-black/90 to-transparent">
                <h2 class="text-xl font-bold">{c.title}</h2>
                <p class="text-xs opacity-70">#{c.category.name} | {c.language}</p>
            </div>
            <div class="absolute bottom-32 right-4 flex flex-col gap-6 items-center">
                <button onclick="likeContent({c.id})" class="bg-black/20 p-3 rounded-full backdrop-blur-md">❤️ <span id="l-{c.id}">{c.likes}</span></button>
                <button onclick="shareContent({c.id})" class="bg-black/20 p-3 rounded-full backdrop-blur-md">📤</button>
            </div>
        </div>'''
    return HttpResponse(html)

@csrf_exempt
def like_content(request, content_id):
    c = get_object_or_404(Content, id=content_id)
    c.likes += 1
    c.rank_score += 5 # Increase rank on like
    c.save()
    return JsonResponse({'likes': c.likes})


@csrf_exempt
def increment_view(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    content.views += 1
    content.watch_time_score += 1 
    content.save(update_fields=['views', 'watch_time_score'])
    
    # Core Optimization: Autorecord scrolling points into active Profile database
    if request.user.is_authenticated:
        request.user.xp += 3
        request.user.level = max(1, (request.user.xp // 100) + 1)
        request.user.save(update_fields=['xp', 'level'])
    else:
        session_key = request.session.session_key
        if session_key:
            UserStreak.objects.filter(session_key=session_key).update(
                total_xp_earned=models.F('total_xp_earned') + 3
            )
            
    return JsonResponse({'views': content.views})


@csrf_exempt
def share_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    content.shares += 1
    content.watch_time_score += 10 
    content.save(update_fields=['shares', 'watch_time_score'])
    return JsonResponse({'status': 'success', 'shares': content.shares})


@login_required
def upload_video_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        video_file = request.FILES.get('video')
        category_id = request.POST.get('category')
        language = request.POST.get('language', 'Hinglish')
        
        if not title or not video_file or not category_id:
            messages.error(request, "Bhai, saare fields bharo pehle!")
            return redirect('/')
            
        category_obj = get_object_or_404(Category, id=category_id)
        
        new_content = Content.objects.create(
            title=title,
            video=video_file,
            category=category_obj,
            language=language
        )
        messages.success(request, f"🚀 '{new_content.title}' uploaded! Gemini background extraction processing active.")
        return redirect('/')
    return redirect('/')


@csrf_exempt
@login_required
def sync_user_xp(request):
    """
    Bridge view to process custom frontend interactive quiz score upgrades directly to the CustomUser.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            points = int(data.get('xp_earned', 0))
            
            user = request.user
            user.xp += points
            user.level = max(1, (user.xp // 100) + 1)
            user.save(update_fields=['xp', 'level'])
            
            return JsonResponse({'status': 'success', 'xp': user.xp, 'level': user.level})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid_method'}, status=405)


@csrf_exempt
@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(CustomUser, id=user_id)
    if request.user != user_to_follow:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    return JsonResponse({'status': 'followed'})

@csrf_exempt
@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(CustomUser, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return JsonResponse({'status': 'unfollowed'})


def stories_view(request):
    # Active stories (not expired)
    active_stories = Story.objects.filter(expires_at__gt=timezone.now()).order_by('-created_at')
    return render(request, 'stories.html', {'stories': active_stories})


@login_required
def upload_story(request):
    if request.method == 'POST':
        video = request.FILES.get('story_video')
        caption = request.POST.get('caption', '')
        
        if video:
            Story.objects.create(
                user=request.user,
                video=video,
                caption=caption
            )
            messages.success(request, "Story uploaded successfully! (24 hours)")
            return redirect('home')
    return redirect('home')



def stories_view(request):
    # Active stories only (not expired)
    active_stories = Story.objects.filter(expires_at__gt=timezone.now()).order_by('user', '-created_at')
    stories_by_user = {}
    for user, stories in groupby(active_stories, key=attrgetter('user')):
        stories_by_user[user] = list(stories)
    
    return render(request, 'stories.html', {
        'stories_by_user': stories_by_user,
        'active_stories': active_stories
    })