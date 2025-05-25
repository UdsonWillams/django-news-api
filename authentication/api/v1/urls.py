from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import CustomTokenObtainPairView, PasswordChangeView, RegisterView

app_name = "authentication"

urlpatterns = [
    # JWT token endpoints
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Registration and password management
    path("register/", RegisterView.as_view(), name="register"),
    path("change-password/", PasswordChangeView.as_view(), name="change_password"),
]
