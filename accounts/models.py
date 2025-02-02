from django.db import models
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    full_name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='users/images/', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    # validation based on:
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return f'{self.full_name}-{self.email}'

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


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
