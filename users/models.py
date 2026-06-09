from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    bio = models.TextField(blank=True, default="")
    profile_pic = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    
    # Beta System Fields
    is_beta_user = models.BooleanField(default=False)
    beta_code_used = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.phone or self.username


class BetaCode(models.Model):
    code = models.CharField(max_length=30, unique=True)
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {'Used' if self.is_used else 'Available'}"

    class Meta:
        verbose_name = "Beta Code"
        verbose_name_plural = "Beta Codes"