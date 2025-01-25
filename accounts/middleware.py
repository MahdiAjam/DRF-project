from rest_framework import status
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import BlockedJTI
from django.core.cache import cache


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
