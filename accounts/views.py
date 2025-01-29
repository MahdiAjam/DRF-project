from drf import settings
from .serializers import UserRegisterSerializer, UserSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import datetime, timezone
from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.response import Response
from rest_framework import status
from .models import BlockedJTI, UserSession
from rest_framework.permissions import IsAuthenticated
from drf import settings
from django.utils.timezone import now


class UserRegisterView(APIView):
    def post(self, request):
        srz_data = UserRegisterSerializer(data=request.POST)
        if srz_data.is_valid():
            srz_data.create(srz_data.validated_data)
            return Response(srz_data.data, status=status.HTTP_201_CREATED)
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user  # Extract the user from the serializer

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            # Set cookies for the tokens
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=settings.SECURE_COOKIES,
                samesite='Strict',
                max_age=3600,
                path='/'
            )

            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=settings.SECURE_COOKIES,
                samesite='Strict',
                max_age=3600 * 24,
                path='/'
            )

            # Decode the refresh token to extract session details
            refresh = RefreshToken(refresh_token)
            jti = refresh['jti']
            expires_at = datetime.fromtimestamp(refresh['exp'], timezone.utc)

            # Extract user agent and IP address
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')
            ip_address = self.get_client_ip(request)

            # Create a new user session
            UserSession.objects.create(
                user=user,  # Use the authenticated user
                jti=jti,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=now(),
                expires_at=expires_at,
                is_active=True
            )

            # Remove token data from response body
            response.data = {}

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the refresh token
            token = RefreshToken(refresh_token)
            jti = token.get('jti')

            # Check if the refresh token is blacklisted
            if BlockedJTI.objects.filter(jti=jti).exists():
                return Response({'detail': 'Refresh token is blacklisted.'}, status=status.HTTP_403_FORBIDDEN)

            # If not blacklisted, proceed with the default behavior
            return super().post(request, *args, **kwargs)

        except TokenError:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_403_FORBIDDEN)


class LogoutView(APIView):
    def post(self, request):
        try:
            # Extract the access and refresh tokens from cookies
            access_token = request.COOKIES.get('access_token')
            refresh_token = request.COOKIES.get('refresh_token')

            # If no tokens are found, return an error
            if not access_token and not refresh_token:
                return Response({'detail': 'No tokens found in cookies.'}, status=status.HTTP_400_BAD_REQUEST)

            user_id = None

            # Block access token
            if access_token:
                token = AccessToken(access_token)
                access_jti = token.get('jti')
                user_id = token.get('user_id')
                BlockedJTI.objects.create(jti=access_jti, user_id=user_id)
                OutstandingToken.objects.filter(jti=access_jti, user_id=user_id).delete()

            # Block refresh token
            if refresh_token:
                refresh = RefreshToken(refresh_token)
                refresh_jti = refresh.get('jti')
                refresh_user_id = refresh.get('user_id')
                BlockedJTI.objects.create(jti=refresh_jti, user_id=refresh_user_id)
                OutstandingToken.objects.filter(jti=refresh_jti, user_id=user_id).delete()

            if user_id:
                UserSession.objects.filter(user_id=user_id, is_active=True).update(is_active=False)

            # Clear the tokens from cookies
            response = Response({'detail': 'Access and refresh tokens successfully blacklisted.'},
                                status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            return response

        except Exception as e:
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class DeactivateTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        jti_to_deactivate = request.data.get('jti')  # JTI مورد نظر
        if not jti_to_deactivate:
            return Response({'detail': 'JTI is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # پیدا کردن توکن مورد نظر
            token = OutstandingToken.objects.filter(jti=jti_to_deactivate, user=request.user).first()

            if not token:
                return Response({'detail': 'Token not found or does not belong to the user.'},
                                status=status.HTTP_404_NOT_FOUND)

            # اضافه کردن به لیست سیاه
            BlacklistedToken.objects.create(token=token)
            return Response({'detail': 'Token has been deactivated.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActiveTokensView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # گرفتن توکن‌های فعال کاربر
        active_tokens = OutstandingToken.objects.filter(
            user=request.user,
            blacklistedtoken__isnull=True,  # فقط توکن‌های بلاک‌نشده
            expires_at__gt=datetime.now(timezone.utc)  # فقط توکن‌های منقضی‌نشده
        )

        # ساختن لیست توکن‌ها برای پاسخ
        tokens_data = [
            {
                "jti": token.jti,
                "created_at": token.created_at,
                "expires_at": token.expires_at
            }
            for token in active_tokens
        ]

        return Response({"active_tokens": tokens_data}, status=200)


class UserSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Retrieve all active sessions for the authenticated user
            sessions = UserSession.objects.filter(user=request.user, is_active=True)

            # Format session data for response
            sessions_data = [
                {
                    "jti": session.jti,
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent,
                    "created_at": session.created_at,
                    "expires_at": session.expires_at,
                    "is_active": session.is_active
                }
                for session in sessions
            ]

            return Response({"sessions": sessions_data}, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error and return an error response
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # permission_classes = [IsAuthenticated]

    # List --> for getting all the resources HTTP METHOD: GET
    # Retrieve --> for getting just one single resource(specific) HTTP METHOD: GET
    # Update --> for updating the whole resource HTTP METHOD: PUT

    # for updating a partition of your resource HTTP METHOD: PATCH
    def partial_update(self, request, pk=None):
        user = self.get_object()
        # we can not use permissions in to a viewsets so, we have to code it manually
        if user != request.user:
            return Response({'permission denied': 'you are not the owner'},
                            status=status.HTTP_403_FORBIDDEN)
        srz_data = self.get_serializer(instance=user, data=request.POST, partial=True)
        if srz_data.is_valid():
            srz_data.save()
            return Response(data=srz_data.data, status=status.HTTP_200_OK)
        return Response(data=srz_data.errors, status=status.HTTP_400_BAD_REQUEST)

    # for deleting your resource HTTP METHOD: DELETE
    def destroy(self, request, pk=None):
        user = self.get_object()
        if user != request.user:
            return Response({'permission denied': 'you are not the owner'},
                            status=status.HTTP_403_FORBIDDEN)
        user.is_active = False
        user.save()
        return Response({'message': 'user deactivated'}, status=status.HTTP_200_OK)
