import logging

from django.db import models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from news.models import News

from .permissions import (
    CanViewNewsContent,
    IsAdminUser,
    IsEditor,
    IsNewsAuthorOrReadOnly,
)
from .serializers import NewsDetailSerializer, NewsListSerializer, NewsSerializer

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        tags=["News"],
        summary="Listar notícias",
        description="Retorna uma lista paginada de notícias, filtrada de acordo com as permissões do usuário atual.",
    ),
    retrieve=extend_schema(
        tags=["News"],
        summary="Obter notícia",
        description="Retorna os detalhes de uma notícia específica se o usuário tiver permissão para acessá-la.",
    ),
    create=extend_schema(
        tags=["News"],
        summary="Criar notícia",
        description="Cria uma nova notícia. Disponível apenas para administradores e editores.",
    ),
    update=extend_schema(
        tags=["News"],
        summary="Atualizar notícia",
        description="Atualiza uma notícia existente. Administradores podem editar qualquer notícia, editores apenas suas próprias.",
    ),
    partial_update=extend_schema(
        tags=["News"],
        summary="Atualizar notícia parcialmente",
        description="Atualiza parcialmente uma notícia existente. Administradores podem editar qualquer notícia, editores apenas suas próprias.",
    ),
    destroy=extend_schema(
        tags=["News"],
        summary="Excluir notícia",
        description="Exclui uma notícia. Administradores podem excluir qualquer notícia, editores apenas suas próprias.",
    ),
)
class NewsViewSet(viewsets.ModelViewSet):
    """
    API endpoint para operações CRUD em notícias.

    Permite listar, criar, editar e excluir notícias conforme as permissões do usuário.
    * Administradores têm acesso total
    * Editores podem gerenciar suas próprias notícias
    * Leitores só podem visualizar notícias publicadas
    """

    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "is_pro_content", "status"]
    search_fields = ["title", "subtitle", "content"]
    ordering_fields = ["publication_date", "created_at", "title"]
    ordering = ["-publication_date", "-created_at"]

    def get_serializer_class(self):
        """Use different serializers for list and detail"""
        if self.action == "list":
            return NewsListSerializer
        elif self.action == "retrieve":
            return NewsDetailSerializer
        return NewsSerializer

    def get_permissions(self):
        """
        Custom permission handling:
        - GET requests: IsAuthenticated + CanViewNewsContent for retrieve
        - POST: IsAuthenticated + (IsAdminUser or IsEditor)
        - PUT/PATCH/DELETE: IsAuthenticated + IsNewsAuthorOrReadOnly
        """
        if self.action == "create":
            permission_classes = [IsAuthenticated, (IsAdminUser | IsEditor)]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsNewsAuthorOrReadOnly]
        elif self.action == "retrieve":
            permission_classes = [IsAuthenticated, CanViewNewsContent]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter queryset based on user type and permissions"""
        user = self.request.user
        queryset = super().get_queryset()

        # Admin can see all news
        if user.is_admin():
            return queryset

        # Editors can see all their own news and published news from others
        if user.is_editor():
            return queryset.filter(
                models.Q(author=user) | models.Q(status=News.StatusChoices.PUBLISHED)
            )

        # Readers can only see published news
        return queryset.filter(status=News.StatusChoices.PUBLISHED)

    def perform_create(self, serializer):
        """Set the author to the current user when creating news"""
        news = serializer.save(author=self.request.user)
        logger.info(
            f"News article created: ID={news.id}, Title='{news.title}', Author={self.request.user.username}"
        )

    @extend_schema(
        tags=["News"],
        summary="Publicar notícia",
        description="Muda o status da notícia para publicado e define a data de publicação atual.",
        responses={
            200: NewsSerializer,
            403: OpenApiResponse(
                description="Permissão negada",
                response={
                    "detail": "Você não tem permissão para publicar esta notícia."
                },
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Action to publish a news article"""
        news = self.get_object()

        # Check if the user has permission to publish
        if not (request.user.is_admin() or news.author == request.user):
            logger.warning(
                f"Unauthorized publish attempt: User={request.user.username}, News ID={news.id}"
            )
            return Response(
                {"detail": "You do not have permission to publish this news."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Publish the news
        news.status = News.StatusChoices.PUBLISHED
        news.publication_date = timezone.now()
        news.save()

        logger.info(f"News published: ID={news.id}, Title='{news.title}'")
        serializer = self.get_serializer(news)
        return Response(serializer.data)
