from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.api.v1.views import UserViewSet

# Router para API v1
router_v1 = DefaultRouter()
router_v1.register(r"users", UserViewSet)

app_name = "users"

urlpatterns = [
    # API v1 routes
    path("api/v1/", include(router_v1.urls)),
]
