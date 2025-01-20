from rest_framework.request import Request
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.views import TokenObtainPairView


class UserRegisterView(APIView):
    def post(self, request):
        srz_data = UserRegisterSerializer(data=request.POST)
        if srz_data.is_valid():
            srz_data.create(srz_data.validated_data)
            return Response(srz_data.data, status=status.HTTP_201_CREATED)
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        user = request.user
        max_tokens = 3
        if OutstandingToken.objects.filter(user=user).count() >= max_tokens:
            raise PermissionDenied('Token limit reached for user.')
        return super().post(request, *args, **kwargs)

class AdminDeleteTokenView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        token_id = request.data.get('token_id')
        try:
            token = OutstandingToken.objects.get(id=token_id)
            token.delete()
            return Response({'message': 'Token deleted successfully'})
        except OutstandingToken.DoesNotExist:
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)
