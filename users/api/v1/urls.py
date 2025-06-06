from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

app_name = "users-api-v1"

router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [path("", include(router.urls))]
