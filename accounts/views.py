from rest_framework.views import APIView
from .serializers import UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class UserRegisterView(APIView):
    def post(self, request):
        srz_data = UserRegisterSerializer(data=request.POST)
        if srz_data.is_valid():
            srz_data.create(srz_data.validated_data)
            return Response(srz_data.data, status=status.HTTP_201_CREATED)
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)

