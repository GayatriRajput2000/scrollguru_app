from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    xp = models.PositiveIntegerField(default=0)
    streak = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    # Fix for clash error
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set', 
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',   
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username