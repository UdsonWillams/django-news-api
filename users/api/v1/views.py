from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .permissions import IsAdminOrSelf, IsAdminUser
from .serializers import UserCreateSerializer, UserDetailSerializer, UserSerializer

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        tags=["Users"],
        summary="Listar usuários",
        description="Retorna uma lista paginada de usuários. Disponível apenas para administradores.",
    ),
    retrieve=extend_schema(
        tags=["Users"],
        summary="Obter usuário",
        description="Retorna os detalhes de um usuário específico. Usuários podem ver apenas seus próprios dados, administradores podem ver qualquer usuário.",
    ),
    create=extend_schema(
        tags=["Users"],
        summary="Criar usuário leitor",
        description="Cria um novo usuário leitor. Disponível para qualquer pessoa autenticada.",
    ),
    update=extend_schema(
        tags=["Users"],
        summary="Atualizar usuário",
        description="Atualiza um usuário existente. Usuários podem atualizar apenas seus próprios dados, administradores podem atualizar qualquer usuário.",
    ),
    partial_update=extend_schema(
        tags=["Users"],
        summary="Atualizar usuário parcialmente",
        description="Atualiza parcialmente um usuário existente. Usuários podem atualizar apenas seus próprios dados, administradores podem atualizar qualquer usuário.",
    ),
    destroy=extend_schema(
        tags=["Users"],
        summary="Excluir usuário",
        description="Exclui um usuário. Disponível apenas para administradores.",
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """API endpoint para gerenciamento de usuários"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering_fields = ["username", "date_joined"]
    ordering = ["-date_joined"]

    def get_serializer_class(self):
        if self.action in ["create", "create_admin", "create_editor"]:
            return UserCreateSerializer
        elif self.action in ["retrieve", "me"]:
            return UserDetailSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Define permissões para diferentes ações:
        - 'create' modificado para permitir qualquer pessoa criar usuários normais
          (a validação do tipo de usuário é feita no serializer)
        """
        if self.action == "list":
            permission_classes = [IsAdminUser]
        elif self.action == "create":
            # Qualquer um pode criar usuário leitor
            permission_classes = [AllowAny]
        elif self.action in ["create_admin", "create_editor"]:
            # Apenas admin pode criar admin ou editor
            permission_classes = [IsAdminUser]
        elif self.action in ["retrieve", "update", "partial_update"]:
            permission_classes = [IsAdminOrSelf]
        elif self.action == "destroy":
            permission_classes = [IsAdminUser]
        elif self.action == "me":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """Cria um usuário leitor (padrão)"""
        # Força o tipo de usuário para 'reader' independentemente do que foi enviado
        data = request.data.copy()
        data["user_type"] = "reader"  # Ajuste para o valor correto no seu sistema

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(
        tags=["Users"],
        summary="Criar usuário administrador",
        description="Cria um novo usuário administrador. Disponível apenas para administradores.",
    )
    @action(detail=False, methods=["post"], url_path="create-admin")
    def create_admin(self, request):
        """Cria um usuário administrador"""
        data = request.data.copy()
        data["user_type"] = "admin"  # Ajuste para o valor correto no seu sistema

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(
        tags=["Users"],
        summary="Criar usuário editor",
        description="Cria um novo usuário editor. Disponível apenas para administradores.",
    )
    @action(detail=False, methods=["post"], url_path="create-editor")
    def create_editor(self, request):
        """Cria um usuário editor"""
        data = request.data.copy()
        data["user_type"] = "editor"

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(
        tags=["Users"],
        summary="Meu perfil",
        description="Retorna os dados do usuário atualmente autenticado.",
        responses={200: UserDetailSerializer},
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user information"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
