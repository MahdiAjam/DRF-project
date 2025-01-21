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

# {
#     "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNzUyODc0NywiaWF0IjoxNzM3NDQyMzQ3LCJqdGkiOiIzOTY1MmFiOTM0NjE0MjM2OTA5ZTNhMGJmNmVmYmZlMiIsInVzZXJfaWQiOjZ9.c7M-80O4kw5sJPe0Kox4DCkCoZk0kM6dPQWtVIn8sxg",
#     "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM3NDQzMjQ3LCJpYXQiOjE3Mzc0NDIzNDcsImp0aSI6IjAyYjgzMDc1ZmZiNjQ1YjRhNDFmMjczMmVhM2ExN2YxIiwidXNlcl9pZCI6Nn0.2AQxxI3pee2u31l2VpE4QfUAwZIidB1exMu3fyVJSvw"
# }