import logging

from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import (  # Adicionando a importação de serializers aqui
    generics,
    serializers,
    status,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer

logger = logging.getLogger(__name__)

User = get_user_model()


@extend_schema(
    tags=["Authentication"],
    summary="Obter token JWT",
    description="Autentica o usuário e retorna um par de tokens de acesso (access) e atualização (refresh).",
    responses={
        200: CustomTokenObtainPairSerializer,
        401: OpenApiResponse(description="Credenciais inválidas"),
    },
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token endpoint que usa nosso serializer aprimorado"""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            username = request.data.get("username", "")
            logger.info(
                f"Successful login: username={username}, IP={self.get_client_ip(request)}"
            )
        else:
            username = request.data.get("username", "")
            logger.warning(
                f"Failed login attempt: username={username}, IP={self.get_client_ip(request)}"
            )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip


@extend_schema(
    tags=["Authentication"],
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário com o tipo 'leitor' por padrão.",
    request=RegisterSerializer,
    responses={
        201: RegisterSerializer,
        400: OpenApiResponse(description="Dados inválidos"),
    },
)
class RegisterView(generics.CreateAPIView):
    """Endpoint para registro de usuários"""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            username = request.data.get("username", "")
            email = request.data.get("email", "")
            logger.info(f"User registered: username={username}, email={email}")
        return response


@extend_schema(
    tags=["Authentication"],
    summary="Alterar senha",
    description="Altera a senha do usuário atualmente autenticado.",
    request=inline_serializer(
        name="PasswordChangeRequest",
        fields={
            "current_password": serializers.CharField(
                help_text="Current user password"
            ),
            "new_password": serializers.CharField(help_text="New password to set"),
        },
    ),
    responses={
        200: OpenApiResponse(description="Senha alterada com sucesso"),
        400: OpenApiResponse(description="Senha atual incorreta"),
    },
)
@extend_schema(tags=["Users"])
class PasswordChangeView(APIView):
    """Endpoint para alteração de senha"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            logger.warning(f"Failed password change attempt: user={user.username}")
            return Response(
                {"current_password": "Incorrect password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        logger.info(f"Password changed successfully: user={user.username}")
        return Response({"detail": "Password changed successfully"})
