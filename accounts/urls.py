from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from rest_framework import routers



app_name = 'accounts'
urlpatterns = [
    path('register/', views.UserRegisterView.as_view()),
    # for login I am using my custom login view.
    path('api/new/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    # for logout I am using my custom logout view.
    path('api/logout/', views.LogoutView.as_view(), name='token_custom_blacklist'),
    path('active-token/', views.ActiveTokensView.as_view(), name='active_token'),
    path('deactive-token/', views.DeactivateTokenView.as_view(), name='deactive_token'),
    path('user-sessions/', views.UserSessionsView.as_view(), name='user_sessions'),
]

router = routers.SimpleRouter()
router.register('user', views.UserViewSet)
urlpatterns += router.urls
