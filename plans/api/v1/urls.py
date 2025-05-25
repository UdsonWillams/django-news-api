from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PlanViewSet, SubscriptionViewSet, VerticalViewSet

app_name = "plans"

router = DefaultRouter()
router.register(r"verticals", VerticalViewSet)
router.register(r"", PlanViewSet)
router.register(r"subscriptions", SubscriptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
