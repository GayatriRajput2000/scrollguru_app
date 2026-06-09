from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Views import kar rahe hain
from content.views import follow_user, home, like_content,increment_view,load_more,share_content, stories_view, unfollow_user, upload_story,upload_video_view
from accounts.views import signup, user_login, profile, user_logout, redirect_to_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='home_redirect'),
    path('home/', home, name='home'),
    path('like/<int:content_id>/', like_content, name='like_content'),
    path('view/<int:content_id>/', increment_view, name='increment_view'),
    path('load-more/', load_more, name='load_more'),
    path('share/<int:content_id>/', share_content, name='share_content'),
    path('upload-video/', upload_video_view, name='upload_video_front'),

    # Auth URLs
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('follow/<int:user_id>/', follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', unfollow_user, name='unfollow_user'),
    path('stories/', stories_view, name='stories'),
    path('upload-story/', upload_story, name='upload_story'),
    path('stories/', stories_view, name='stories'),
]

# Important: Media files (videos) serve karne ke liye
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)