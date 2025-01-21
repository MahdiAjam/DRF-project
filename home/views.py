from rest_framework.views import APIView
from django.contrib.auth.models import User
from .serializers import PersonSerializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class Home(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        persons = User.objects.all()
        srz_data = PersonSerializers(instance=persons, many=True)
        return Response(data=srz_data.data, status=status.HTTP_200_OK)
