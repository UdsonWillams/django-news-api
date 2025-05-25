import pytest
from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.django_db
class TestAuthAPI:
    """Testes para as funcionalidades de autenticação da API"""

    def test_change_password(
        self, api_client: APIClient, existing_user: CustomUser, user_data: dict
    ):
        """Testa a funcionalidade de alteração de senha do usuário"""
        # Login para obter token
        login_url = "/api/v1/auth/token/"
        login_response = api_client.post(
            login_url,
            {"username": user_data["username"], "password": user_data["password"]},
        )
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.data["access"]

        # Mudar senha
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        change_url = "/api/v1/auth/change-password/"
        new_password = "newpassword123"
        data = {
            "current_password": user_data["password"],
            "new_password": new_password,
        }

        response = api_client.post(change_url, data)
        assert response.status_code == status.HTTP_200_OK

        # Verificar se a senha foi alterada tentando fazer login com a nova senha
        api_client.credentials()  # Limpa credenciais
        verification_response = api_client.post(
            login_url, {"username": user_data["username"], "password": new_password}
        )
        assert verification_response.status_code == status.HTTP_200_OK
