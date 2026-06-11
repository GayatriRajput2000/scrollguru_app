from django.db import models
from django.contrib.auth.models import AbstractUser

from core import settings


class BetaCode(models.Model):
    code = models.CharField(max_length=30, unique=True)
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {'Used' if self.is_used else 'Available'}"

    class Meta:
        verbose_name = "Beta Code"
        verbose_name_plural = "Beta Codes"