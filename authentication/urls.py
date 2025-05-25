from django.urls import include, path

app_name = "authentication"

urlpatterns = [
    # API v1 endpoints
    path("api/v1/auth/", include("authentication.api.v1.urls")),
    # Adicione aqui futuras URLs de interface web, se necessário
    # path('login/', include('authentication.web.urls')),
]
