from django.contrib import admin
from .models import Content, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'has_quiz', 'views', 'likes']
    list_filter = ['category', 'has_quiz']
    fieldsets = [
        ('Core Info', {'fields': ['title', 'video', 'category', 'language', 'description']}),
        ('Duolingo Quiz Feature', {'fields': ['has_quiz', 'quiz_question', 'option_a', 'option_b', 'correct_option']}),
        ('Stats (Read Only)', {'fields': ['video_url', 'views', 'likes', 'shares', 'watch_time_score']}),
    ]
    readonly_fields = ['video_url', 'views', 'likes', 'shares', 'watch_time_score']