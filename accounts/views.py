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
from .models import BlockedJTI


class UserRegisterView(APIView):
    def post(self, request):
        srz_data = UserRegisterSerializer(data=request.POST)
        if srz_data.is_valid():
            srz_data.create(srz_data.validated_data)
            return Response(srz_data.data, status=status.HTTP_201_CREATED)
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")

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
            access_token = request.data.get('access')
            refresh_token = request.data.get('refresh')

            # Block access token
            if access_token:
                token = AccessToken(access_token)
                access_jti = token.get('jti')
                user_id = token.get('user_id')
                BlockedJTI.objects.create(jti=access_jti, user_id=user_id)

            # Block refresh token
            if refresh_token:
                refresh = RefreshToken(refresh_token)
                refresh_jti = refresh.get('jti')
                refresh_user_id = refresh.get('user_id')
                BlockedJTI.objects.create(jti=refresh_jti, user_id=refresh_user_id)

            return Response({'detail': 'Access and refresh tokens successfully blacklisted.'},
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Something went wrong: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)



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
