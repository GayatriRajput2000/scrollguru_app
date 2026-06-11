import os
from django.db import models
from django.utils.text import slugify
import google.generativeai as genai
from django.utils.text import slugify
from django.utils import timezone


LANGUAGE_CHOICES = [
    ('Hindi', 'Hindi'),
    ('English', 'English'),
    ('Hinglish', 'Hinglish'),
]


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Content(models.Model):
    title = models.CharField(max_length=200)
    video = models.FileField(upload_to='videos/')
    video_url = models.URLField(blank=True, null=True, max_length=500)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default="Hindi")

    # ---------------- AI CONTENT ----------------
    description = models.TextField(blank=True)

    has_quiz = models.BooleanField(default=False)
    quiz_question = models.CharField(max_length=255, blank=True, null=True)
    option_a = models.CharField(max_length=100, blank=True, null=True)
    option_b = models.CharField(max_length=100, blank=True, null=True)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B')],
        blank=True,
        null=True
    )

    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    watch_time_score = models.IntegerField(default=0)
    rank_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rank_score', '-watch_time_score', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if self.video and not self.video_url:
            self.video_url = self.video.url
            Content.objects.filter(id=self.id).update(video_url=self.video.url)

        if is_new and self.video:
            try:
                self.generate_ai_metadata()
            except Exception as e:
                print("AI Error:", e)
    def generate_ai_metadata(self):
        api_key = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
        if api_key == "YOUR_GEMINI_API_KEY":
            self.description = f"Learn {self.title} in seconds 🚀 #ScrollGuru"
            self.save(update_fields=['description'])
            return
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are an AI for an educational reels app.

        Topic: {self.title}
        Category: {self.category.name}

        Generate:

        1. One short viral description (max 80 chars + 2 hashtags)
        2. One quiz question with 2 options and correct answer

        Format EXACTLY:

        DESCRIPTION: ...
        ---
        QUESTION: ...
        A: ...
        B: ...
        CORRECT: A or B
        """

        response = model.generate_content(prompt)
        text = response.text
        try:
            parts = text.split('---')
            desc = parts[0].replace("DESCRIPTION:", "").strip()
            quiz = parts[1].strip()

            lines = [l.strip() for l in quiz.split('\n') if l.strip()]

            question = lines[0].replace("QUESTION:", "").strip()
            a = lines[1].replace("A:", "").strip()
            b = lines[2].replace("B:", "").strip()
            correct = lines[3].replace("CORRECT:", "").strip()

            self.description = desc
            self.has_quiz = True
            self.quiz_question = question
            self.option_a = a
            self.option_b = b
            self.correct_option = correct
            self.save(update_fields=[
                'description',
                'has_quiz',
                'quiz_question',
                'option_a',
                'option_b',
                'correct_option'
            ])

        except Exception:
            self.description = f"Master {self.title} step by step 🚀 #learn"
            self.save(update_fields=['description'])


class UserStreak(models.Model):
    session_key = models.CharField(max_length=100, unique=True)
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_login_date = models.DateField(auto_now=True)
    total_xp_earned = models.PositiveIntegerField(default=0)
    last_reward_claimed = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Streak {self.current_streak} - {self.session_key[:8]}"


class Follow(models.Model):
    follower = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} follows {self.following}"
    

class Story(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='stories')
    video = models.FileField(upload_to='stories/')
    caption = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    class Meta:
        ordering = ['-created_at']