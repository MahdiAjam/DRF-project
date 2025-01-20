from django.contrib import admin
#
# from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
#
#
# @admin.register(OutstandingToken)
# class OutstandingTokenAdmin(admin.ModelAdmin):
#     list_display = ('user', 'jti', 'created_at', 'expires_at')
#
#     def has_delete_permission(self, request, obj=None):
#         return True  # this allows admin to delete tokens
#
#
# @admin.register(BlacklistedToken)
# class BlacklistedTokenAdmin(admin.ModelAdmin):
#     list_display = ('token', 'blacklisted_at')
