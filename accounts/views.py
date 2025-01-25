from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from .utils import CustomAccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import datetime, timezone
from rest_framework import viewsets
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated


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

                user = token['user_id']
                recent_token = OutstandingToken.objects.filter(user_id=user).order_by('-created_at').first()
                if recent_token:
                    BlacklistedToken.objects.create(token=recent_token)

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

# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNzY0NjgzNiwiaWF0IjoxNzM3NTYwNDM2LCJqdGkiOiIyYzFkZDM1Y2Y4NTc0ODUyOTFhZmJjZjZmNzg2OWY4NSIsInVzZXJfaWQiOjd9.mkC1tkC7s9ncGryBIP4gaszP35EbiYhE2gUYOxX944w
