from rest_framework import status
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import BlockedJTI
from django.core.cache import cache
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

class CheckBlockedTokensMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Extract the authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]  # Extract the token
            try:
                access_token = AccessToken(token)
                jti = access_token.get('jti')

                # Check if the JTI is blocked
                if cache.get(f'blocked_jti_{jti}') or BlockedJTI.objects.filter(jti=jti).exists():
                    # Cache the blocked JTI to avoid repeated DB lookups
                    cache.set(f'blocked_jti_{jti}', True, timeout=3600)  # Cache for 1 hour
                    return JsonResponse({'detail': 'Token is blocked.'}, status=status.HTTP_403_FORBIDDEN)

            except TokenError:
                return JsonResponse({'detail': 'Invalid token.'}, status=status.HTTP_403_FORBIDDEN)

        return None


class CheckBlockedJTIMiddleware(MiddlewareMixin):
    MAX_ACTIVE_TOKENS = 3  # حداکثر تعداد لاگین‌های مجاز برای هر کاربر

    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                access_token = AccessToken(token)
                jti = access_token.get('jti')
                user_id = access_token.get('user_id')

                # بررسی بلاک بودن JTI
                if BlockedJTI.objects.filter(jti=jti).exists():
                    return JsonResponse({'detail': 'Access token is blocked'}, status=403)

                # بررسی تعداد لاگین‌های فعال
                active_tokens = OutstandingToken.objects.filter(user_id=user_id, blacklistedtoken__isnull=True)
                if active_tokens.count() > self.MAX_ACTIVE_TOKENS:
                    return JsonResponse(
                        {'detail': 'Maximum active logins exceeded. Please log out from another session.'},
                        status=403)

            except Exception as e:
                return JsonResponse({'detail': 'Invalid token', 'error': str(e)}, status=403)

        return None


class CheckAccessTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return JsonResponse({'detail': 'Access token is missing in cookies'}, status=status.HTTP_403_FORBIDDEN)

        try:
            token = AccessToken(access_token)

            request.user = token.user

        except Exception as e:
            return JsonResponse({'detail': 'Invalid access token.', 'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

        return None
