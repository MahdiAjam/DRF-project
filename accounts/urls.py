from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

app_name = 'accounts'
urlpatterns = [
    path('register/', views.UserRegisterView.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
]

# {
#     "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNzUyMTkxMywiaWF0IjoxNzM3NDM1NTEzLCJqdGkiOiI0MjA3YjMzNzE0N2Q0ODk0YmNjNWU4M2IzMDJiNzQxMCIsInVzZXJfaWQiOjN9.5S9zKG2TIKkTRVC4Fb740O617o9MgVQFrvGSf9E_XVY",
#     "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM3NDM1ODEzLCJpYXQiOjE3Mzc0MzU1MTMsImp0aSI6IjQxMWFjMWFjZTYxNTRlYTViZTgwNGE1NjU0NzRmMWJmIiwidXNlcl9pZCI6M30.P4WfBGd2Aul3V1-WqOHDYaArruO_PqhK9IJX_i5ppi8"
# }