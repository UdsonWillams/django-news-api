from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NewsViewSet

app_name = "api-v1"

router = DefaultRouter()
router.register(r"articles", NewsViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
