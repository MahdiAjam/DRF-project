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
