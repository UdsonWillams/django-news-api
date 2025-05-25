import pytest
from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser

BASE_URL = "/api/v1/users/"
ME_URL = f"{BASE_URL}me/"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.django_db
class TestUserAPI:
    def test_me_endpoint(
        self, api_client, reader_user, reader_token, plan, subscription
    ):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")
        url = "/api/v1/users/me/"

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == reader_user.username
        assert response.json()["email"] == reader_user.email

        assert response.json()["active_subscription"]["status"] == subscription.status
        assert response.json()["active_subscription"]["plan_type"] == plan.plan_type
        assert response.json()["active_subscription"]["plan_name"] == plan.name
        assert response.json()["user_type"] == reader_user.user_type

    def test_list_users_admin(
        self,
        api_client: APIClient,
        admin_token: str,
        admin_user: CustomUser,
        reader_user: CustomUser,
        editor_user: CustomUser,
    ):
        """Admin pode listar todos os usuários"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        response = api_client.get(BASE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["count"] >= 3
        )  # Deve encontrar pelo menos os 3 usuários criados nas fixtures

    def test_list_users_reader_forbidden(
        self, api_client: APIClient, reader_token: str, admin_user: CustomUser
    ):
        """Leitores não podem listar todos os usuários"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")
        response = api_client.get(BASE_URL)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_reader_user(self, api_client: APIClient):
        """Qualquer pessoa pode criar conta de leitor"""
        data = {
            "username": "newreader",
            "email": "newreader@test.com",
            "password": "securepass123",
            "user_type": "reader",
            "first_name": "New",
            "last_name": "Reader",
        }

        response = api_client.post(BASE_URL, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["username"] == "newreader"
        assert response.data["user_type"] == "reader"
        assert "password" not in response.data

    def test_create_admin_user_by_admin(
        self,
        api_client: APIClient,
        admin_staff_token: str,
        admin_staff_user: CustomUser,
    ):
        """Admin pode criar usuário admin"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_staff_token}")
        data = {
            "username": "newadmin",
            "email": "newadmin@test.com",
            "password": "secureadmin123",
            "user_type": "admin",
            "first_name": "New",
            "last_name": "Admin",
        }

        response = api_client.post(f"{BASE_URL}create-admin/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user_type"] == "admin"

    def test_create_admin_user_by_reader_return_forbidden(
        self, api_client: APIClient, reader_token: str, reader_user: CustomUser
    ):
        """Leitor não pode criar usuário admin"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")
        data = {
            "username": "adminattempt",
            "email": "adminattempt@test.com",
            "password": "attempt123",
            "user_type": "admin",
        }

        response = api_client.post(f"{BASE_URL}create-admin/", data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_retrieve_own_user(
        self,
        api_client: APIClient,
        reader_user: CustomUser,
        reader_token: str,
        plan,
        subscription,
    ):
        """Usuário pode ver seus próprios detalhes"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")
        url = f"{BASE_URL}{reader_user.id}/"

        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == reader_user.username
        assert "active_subscription" in response.data

    def test_retrieve_other_user_by_admin(
        self, api_client: APIClient, admin_token: str, reader_user: CustomUser
    ):
        """Admin pode ver detalhes de qualquer usuário"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = f"{BASE_URL}{reader_user.id}/"

        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == reader_user.username

    def test_retrieve_other_user_by_reader_forbidden(
        self, api_client: APIClient, reader_token: str, editor_user: CustomUser
    ):
        """Leitor não pode ver detalhes de outros usuários"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")
        url = f"{BASE_URL}{editor_user.id}/"

        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_own_user(
        self, api_client: APIClient, reader_user: CustomUser, reader_token: str
    ):
        """Usuário pode atualizar seus próprios dados"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")
        url = f"{BASE_URL}{reader_user.id}/"
        data = {"first_name": "Updated", "last_name": "Name"}

        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
        assert response.data["last_name"] == "Name"

    def test_delete_user_by_admin(
        self, api_client: APIClient, admin_token: str, reader_user: CustomUser
    ):
        """Admin pode excluir usuários"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = f"{BASE_URL}{reader_user.id}/"

        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Confirma que o usuário foi realmente excluído
        assert not CustomUser.objects.filter(id=reader_user.id).exists()

    def test_delete_user_by_reader_forbidden(
        self, api_client: APIClient, reader_token: str, editor_user: CustomUser
    ):
        """Leitor não pode excluir usuários"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")
        url = f"{BASE_URL}{editor_user.id}/"

        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        # Confirma que o usuário não foi excluído
        assert CustomUser.objects.filter(id=editor_user.id).exists()
