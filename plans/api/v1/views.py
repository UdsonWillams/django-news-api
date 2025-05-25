from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from plans.models import Plan, Subscription, Vertical

from .permissions import IsAdminUser
from .serializers import (
    PlanCreateUpdateSerializer,
    PlanSerializer,
    SubscriptionCreateUpdateSerializer,
    SubscriptionSerializer,
    VerticalSerializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Verticals"],
        summary="Listar verticais",
        description="Retorna uma lista de todas as verticais de conteúdo disponíveis.",
    ),
    retrieve=extend_schema(
        tags=["Verticals"],
        summary="Obter vertical",
        description="Retorna os detalhes de uma vertical específica.",
    ),
    create=extend_schema(
        tags=["Verticals"],
        summary="Criar vertical",
        description="Cria uma nova vertical de conteúdo. Disponível apenas para administradores.",
    ),
    update=extend_schema(
        tags=["Verticals"],
        summary="Atualizar vertical",
        description="Atualiza uma vertical existente. Disponível apenas para administradores.",
    ),
    partial_update=extend_schema(
        tags=["Verticals"],
        summary="Atualizar vertical parcialmente",
        description="Atualiza parcialmente uma vertical existente. Disponível apenas para administradores.",
    ),
    destroy=extend_schema(
        tags=["Verticals"],
        summary="Excluir vertical",
        description="Exclui uma vertical. Disponível apenas para administradores.",
    ),
)
class VerticalViewSet(viewsets.ModelViewSet):
    """API endpoint para gerenciamento de verticais de conteúdo"""

    queryset = Vertical.objects.all()
    serializer_class = VerticalSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


@extend_schema_view(
    list=extend_schema(
        tags=["Plans"],
        summary="Listar planos",
        description="Retorna uma lista de todos os planos de assinatura disponíveis.",
    ),
    retrieve=extend_schema(
        tags=["Plans"],
        summary="Obter plano",
        description="Retorna os detalhes de um plano de assinatura específico.",
    ),
    create=extend_schema(
        tags=["Plans"],
        summary="Criar plano",
        description="Cria um novo plano de assinatura. Disponível apenas para administradores.",
    ),
    update=extend_schema(
        tags=["Plans"],
        summary="Atualizar plano",
        description="Atualiza um plano existente. Disponível apenas para administradores.",
    ),
    partial_update=extend_schema(
        tags=["Plans"],
        summary="Atualizar plano parcialmente",
        description="Atualiza parcialmente um plano existente. Disponível apenas para administradores.",
    ),
    destroy=extend_schema(
        tags=["Plans"],
        summary="Excluir plano",
        description="Exclui um plano. Disponível apenas para administradores.",
    ),
)
class PlanViewSet(viewsets.ModelViewSet):
    """API endpoint para gerenciamento de planos de assinatura"""

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["plan_type", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "price"]
    ordering = ["price"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            # Permite acesso anônimo para listar e visualizar planos
            permission_classes = []
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PlanCreateUpdateSerializer
        return PlanSerializer

    @extend_schema(
        tags=["Plans"],
        summary="Obter assinaturas de um plano",
        description="Retorna todas as assinaturas associadas a um plano específico.",
        responses={200: SubscriptionSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def subscriptions(self, request, pk=None):
        """Get all subscriptions for a plan"""
        plan = self.get_object()
        queryset = plan.subscriptions.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=["Subscriptions"],
        summary="Listar assinaturas",
        description="Retorna uma lista de assinaturas. Administradores veem todas, outros usuários apenas suas próprias.",
    ),
    retrieve=extend_schema(
        tags=["Subscriptions"],
        summary="Obter assinatura",
        description="Retorna os detalhes de uma assinatura específica.",
    ),
    create=extend_schema(
        tags=["Subscriptions"],
        summary="Criar assinatura",
        description="Cria uma nova assinatura. Disponível apenas para administradores.",
    ),
    update=extend_schema(
        tags=["Subscriptions"],
        summary="Atualizar assinatura",
        description="Atualiza uma assinatura existente. Disponível apenas para administradores.",
    ),
    partial_update=extend_schema(
        tags=["Subscriptions"],
        summary="Atualizar assinatura parcialmente",
        description="Atualiza parcialmente uma assinatura existente. Disponível apenas para administradores.",
    ),
    destroy=extend_schema(
        tags=["Subscriptions"],
        summary="Excluir assinatura",
        description="Exclui uma assinatura. Disponível apenas para administradores.",
    ),
)
class SubscriptionViewSet(viewsets.ModelViewSet):
    """API endpoint para gerenciamento de assinaturas"""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["user", "plan", "status"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["-created_at"]

    def get_permissions(self):
        # Apenas admins podem modificar assinaturas
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filtragem automática - admins veem tudo, outros só veem suas assinaturas"""
        user = self.request.user
        if user.is_admin():
            return Subscription.objects.all()
        return Subscription.objects.filter(user=user)

    def get_serializer_class(self):
        """
        Retorna o serializer apropriado:
        - SubscriptionCreateUpdateSerializer para criação e atualização
        - SubscriptionSerializer para visualização
        """
        if self.action in ["create", "update", "partial_update"]:
            return SubscriptionCreateUpdateSerializer
        return SubscriptionSerializer

    @extend_schema(
        tags=["Subscriptions"],
        summary="Minhas assinaturas",
        description="Retorna as assinaturas do usuário atualmente autenticado.",
        responses={200: SubscriptionSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="my-subscriptions")
    def my_subscriptions(self, request):
        """
        Get current user's subscriptions
        """
        queryset = Subscription.objects.filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
