from django.urls import include, path

app_name = "news"

urlpatterns = [
    # API v1 endpoints
    path("api/v1/news/", include("news.api.v1.urls")),
    # Adicione aqui futuras URLs de interface web, se necessário
    # path('news/', include('news.web.urls')),
]
