from django.contrib import admin
from .models import BlockedJTI, UserSession

admin.site.register(BlockedJTI)
admin.site.register(UserSession)