from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from plans.models import Plan, Subscription, Vertical
from users.models import CustomUser

# Constantes de URL
PLANS_BASE_URL = "/api/v1/plans/"
VERTICALS_BASE_URL = "/api/v1/plans/verticals/"
SUBSCRIPTIONS_BASE_URL = "/api/v1/plans/subscriptions/"
MY_SUBSCRIPTIONS_URL = f"{SUBSCRIPTIONS_BASE_URL}my-subscriptions/"


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.django_db
class TestPlansAPI:
    def test_list_plans_anonymous(self, api_client: APIClient, plan: Plan):
        """Usuários anônimos podem listar planos públicos"""
        response = api_client.get(PLANS_BASE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_retrieve_plan_anonymous(self, api_client: APIClient, plan: Plan):
        """Usuários anônimos podem ver detalhes de planos específicos"""
        url = f"{PLANS_BASE_URL}{plan.id}/"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == plan.id
        assert response.data["name"] == plan.name
        assert float(response.data["price"]) == plan.price

    def test_create_plan_admin(
        self, api_client: APIClient, admin_token: str, vertical: Vertical
    ):
        """Administradores podem criar planos"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        data = {
            "name": "Novo Plano Premium",
            "slug": "novo-plano-premium",
            "description": "Um plano premium para teste",
            "plan_type": "pro",
            "price": "199.99",
            "verticals": [vertical.id],
            "is_active": True,
        }

        response = api_client.post(PLANS_BASE_URL, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Novo Plano Premium"
        assert Plan.objects.filter(slug="novo-plano-premium").exists()

    def test_create_plan_reader_forbidden(
        self, api_client: APIClient, reader_token: str
    ):
        """Leitores não podem criar planos"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")
        data = {
            "name": "Plano Não Permitido",
            "slug": "plano-nao-permitido",
            "plan_type": "info",
            "price": "50.00",
        }

        response = api_client.post(PLANS_BASE_URL, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_plan_admin(
        self, api_client: APIClient, admin_token: str, plan: Plan
    ):
        """Administradores podem atualizar planos"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = f"{PLANS_BASE_URL}{plan.id}/"
        data = {"price": "149.99", "name": "Plano Atualizado"}

        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        plan.refresh_from_db()
        assert plan.name == "Plano Atualizado"
        assert str(plan.price) == "149.99"

    def test_delete_plan_admin(
        self, api_client: APIClient, admin_token: str, plan: Plan
    ):
        """Administradores podem excluir planos"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = f"{PLANS_BASE_URL}{plan.id}/"

        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Plan.objects.filter(id=plan.id).exists()

    # Testes para Verticais (Verticals)

    def test_list_verticals(self, api_client: APIClient, vertical: Vertical):
        """Qualquer usuário pode listar verticais"""
        response = api_client.get(VERTICALS_BASE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_create_vertical_admin(self, api_client: APIClient, admin_token: str):
        """Administradores podem criar verticais"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        data = {
            "name": "Nova Vertical",
            "slug": "energia",
            "description": "Vertical para conteúdo sobre energia",
        }

        response = api_client.post(VERTICALS_BASE_URL, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Vertical.objects.filter(slug="energia").exists()

    # Testes para Assinaturas (Subscriptions)

    def test_list_subscriptions_admin(
        self, api_client: APIClient, admin_token: str, subscription: Subscription
    ):
        """Administradores podem listar todas as assinaturas"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        response = api_client.get(SUBSCRIPTIONS_BASE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_list_subscriptions_reader(
        self, api_client: APIClient, reader_token: str, subscription: Subscription
    ):
        """Leitores podem listar apenas suas próprias assinaturas"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")
        response = api_client.get(SUBSCRIPTIONS_BASE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == subscription.id
        assert response.data["results"][0]["user"] == subscription.user.id
        assert response.data["results"][0]["plan"]["id"] == subscription.plan.id
        assert response.data["results"][0]["status"] == subscription.status

    def test_create_subscription_admin(
        self,
        api_client: APIClient,
        admin_token: str,
        reader_user: CustomUser,
        plan: Plan,
    ):
        """Administradores podem criar assinaturas para outros usuários"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        data = {
            "user": reader_user.id,
            "plan": plan.id,
            "status": "active",
            "start_date": timezone.now().isoformat(),
            "end_date": (timezone.now() + timedelta(days=30)).isoformat(),
        }

        response = api_client.post(SUBSCRIPTIONS_BASE_URL, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Subscription.objects.filter(user=reader_user, plan=plan).exists()

    def test_retrieve_subscription_admin(
        self, api_client: APIClient, admin_token: str, subscription: Subscription
    ):
        """Administradores podem ver detalhes de assinaturas"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = f"{SUBSCRIPTIONS_BASE_URL}{subscription.id}/"

        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == subscription.id
        assert response.data["user"] == subscription.user.id

    def test_get_reader_subscriptions(
        self,
        api_client: APIClient,
        reader_user: CustomUser,
        reader_token: str,
        subscription: Subscription,
    ):
        """Leitores podem ver suas próprias assinaturas"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")

        response = api_client.get(MY_SUBSCRIPTIONS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["id"] == subscription.id
        assert response.data["results"][0]["user"] == reader_user.id
        assert response.data["results"][0]["user_username"] == reader_user.username
        assert response.data["results"][0]["status"] == subscription.status
        assert response.data["results"][0]["plan"]["id"] == subscription.plan.id

    def test_update_subscription_admin(
        self, api_client: APIClient, admin_token: str, subscription: Subscription
    ):
        """Administradores podem atualizar assinaturas"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = f"{SUBSCRIPTIONS_BASE_URL}{subscription.id}/"

        # Alterar status da assinatura
        data = {"status": "cancelled"}
        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        subscription.refresh_from_db()
        assert subscription.status == "cancelled"

    def test_filter_plans_by_vertical(
        self, api_client: APIClient, plan: Plan, vertical: Vertical
    ):
        """Usuários podem filtrar planos por vertical"""
        url = f"{PLANS_BASE_URL}?vertical={vertical.id}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1
        assert response.data["results"][0]["id"] == plan.id

    def test_filter_plans_by_type(self, api_client: APIClient, plan: Plan):
        """Usuários podem filtrar planos por tipo"""
        url = f"{PLANS_BASE_URL}?plan_type={plan.plan_type}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1
        found = any(p["id"] == plan.id for p in response.data["results"])
        assert found
