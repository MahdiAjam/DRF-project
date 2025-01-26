from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken


class BlockedJTI(models.Model):
    jti = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)

    @property
    def user_from_token(self):
        try:
            token = AccessToken(self.jti)
            user_id = token.get('user_id')
            return User.objects.get(id=user_id)
        except (User.DoesNotExist, KeyError, ValueError):
            return None

    def __str__(self):
        return f'blocked jti: {self.jti} (User: {self.user.username})'


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    jti = models.CharField(max_length=255, unique=True)  # شناسه JTI
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # آدرس IP
    user_agent = models.TextField(null=True, blank=True)  # اطلاعات User Agent
    created_at = models.DateTimeField(default=now)  # تاریخ و زمان ایجاد توکن
    expires_at = models.DateTimeField()  # تاریخ انقضای توکن
    is_active = models.BooleanField(default=True)  # وضعیت نشست

    def __str__(self):
        return f"Session for {self.user.username} (JTI: {self.jti})"
