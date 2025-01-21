from rest_framework.views import APIView
from .serializers import UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .utils import CustomAccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import datetime, timezone


class UserRegisterView(APIView):
    def post(self, request):
        srz_data = UserRegisterSerializer(data=request.POST)
        if srz_data.is_valid():
            srz_data.create(srz_data.validated_data)
            return Response(srz_data.data, status=status.HTTP_201_CREATED)
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            access_token = request.data.get('access')

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            if access_token:
                access = CustomAccessToken(access_token)
                token_obj = OutstandingToken.objects.filter(token=str(access)).first()
                if token_obj:
                    BlacklistedToken.objects.create(token=token_obj)

            return Response({'detail': 'Tokens successfully blacklisted.'}, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({'error': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    MAX_TOKENS_PER_USER = 3

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            OutstandingToken.objects.filter(user=user, expires_at__lt=datetime.now(timezone.utc)).delete()

            user_tokens = OutstandingToken.objects.filter(user=user)
            if user_tokens.count() >= self.MAX_TOKENS_PER_USER:
                return Response(
                    {'detail': 'Token limit exceeded. Please log out from another session to create a new token'},
                    status=status.HTTP_403_FORBIDDEN)

        response = super().post(request, *args, **kwargs)
        return response
