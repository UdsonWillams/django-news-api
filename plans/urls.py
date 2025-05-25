from django.urls import include, path
from rest_framework.routers import DefaultRouter

from plans.api.v1.views import SubscriptionViewSet, VerticalViewSet

# Router para API v1
router_v1 = DefaultRouter()
router_v1.register(r"plans/verticals", VerticalViewSet)
router_v1.register(r"plans/subscriptions", SubscriptionViewSet)

app_name = "plans"

urlpatterns = [
    # API v1 routes
    path("api/v1/", include(router_v1.urls)),
    # API v1 endpoints
    path("api/v1/plans/", include("plans.api.v1.urls")),
    # Adicione aqui futuras URLs de interface web, se necessário
    # path('subscription/', include('plans.web.urls')),
]
