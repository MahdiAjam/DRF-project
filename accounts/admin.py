from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, BlockedJTI, UserSession


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'phone_number', 'full_name', 'is_admin')
    list_filter = ('is_admin', 'is_active')
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        ('Main', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        ('Add User',
         {'fields': ('phone_number', 'email', 'full_name', 'password1', 'password2', 'is_admin', 'is_active')}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(BlockedJTI)
admin.site.register(UserSession)
