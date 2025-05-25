from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from news.models import News
from plans.models import Plan, Subscription, Vertical
from users.models import CustomUser

# Constantes para senhas
ADMIN_PASSWORD = "adminpass123"
EDITOR_PASSWORD = "editorpass123"
READER_PASSWORD = "readerpass123"
TEST_USER_PASSWORD = "password123"

# Constantes para usernames
ADMIN_USERNAME = "testadmin"
ADMIN_STAFF_USERNAME = "testadminstaff"
EDITOR_USERNAME = "editor"
READER_USERNAME = "reader"
TEST_USERNAME = "testuser"


@pytest.fixture
def api_client():
    """Fixture que fornece um cliente API para testes"""
    return APIClient()


@pytest.fixture
def admin_user():
    """Fixture que cria e retorna um usuário administrador"""
    return CustomUser.objects.create_user(
        username=ADMIN_USERNAME,
        email="admin@test.com",
        password=ADMIN_PASSWORD,
        user_type=CustomUser.ADMIN,
    )


@pytest.fixture
def admin_staff_user():
    """Fixture que cria e retorna um usuário administrador com privilégios de staff"""
    return CustomUser.objects.create_user(
        username=ADMIN_STAFF_USERNAME,
        email="adminstaff@test.com",
        password=ADMIN_PASSWORD,
        user_type=CustomUser.ADMIN,
        is_staff=True,
    )


@pytest.fixture
def editor_user():
    """Fixture que cria e retorna um usuário editor"""
    return CustomUser.objects.create_user(
        username=EDITOR_USERNAME,
        email="editor@test.com",
        password=EDITOR_PASSWORD,
        user_type=CustomUser.EDITOR,
    )


@pytest.fixture
def reader_user():
    """Fixture que cria e retorna um usuário leitor"""
    return CustomUser.objects.create_user(
        username=READER_USERNAME,
        email="reader@test.com",
        password=READER_PASSWORD,
        user_type=CustomUser.READER,
    )


@pytest.fixture
def user_data():
    """Fixture que retorna dados para criar um usuário de teste"""
    return {
        "username": TEST_USERNAME,
        "email": "testuser@test.com",
        "password": TEST_USER_PASSWORD,
    }


@pytest.fixture
def existing_user(user_data):
    """Fixture que cria um usuário com os dados de user_data"""
    return CustomUser.objects.create_user(
        username=user_data["username"],
        email=user_data["email"],
        password=user_data["password"],
    )


@pytest.fixture
def vertical():
    """Fixture que cria uma vertical de teste"""
    return Vertical.objects.create(
        name="Test Vertical", slug="poder", description="Test Description"
    )


@pytest.fixture
def plan(vertical):
    """Fixture que cria um plano de teste"""
    plan = Plan.objects.create(
        name="Test Plan", slug="test-plan", plan_type="pro", price=100.00
    )
    plan.verticals.add(vertical)
    return plan


@pytest.fixture
def subscription(reader_user, plan):
    """Fixture que cria uma assinatura de teste"""
    return Subscription.objects.create(
        user=reader_user,
        plan=plan,
        status="active",
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=30),
    )


@pytest.fixture
def published_news(editor_user):
    """Fixture que cria uma notícia publicada"""
    return News.objects.create(
        title="Test Published News",
        content="This is test content",
        author=editor_user,
        category="poder",
        status=News.StatusChoices.PUBLISHED,
        publication_date=timezone.now(),
    )


@pytest.fixture
def unpublished_news(editor_user):
    """Fixture que cria uma notícia não publicada (rascunho)"""
    return News.objects.create(
        title="Test Draft News",
        content="This is unpublished draft content",
        author=editor_user,
        category="poder",
        status=News.StatusChoices.DRAFT,
        publication_date=None,
    )


@pytest.fixture
def admin_token(api_client, admin_user):
    """Fixture que retorna um token JWT para o usuário administrador"""
    url = "/api/v1/auth/token/"
    response = api_client.post(
        url, {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    return response.json()["access"]


@pytest.fixture
def admin_staff_token(api_client, admin_staff_user):
    """Fixture que retorna um token JWT para o usuário administrador com privilégios de staff"""
    url = "/api/v1/auth/token/"
    response = api_client.post(
        url, {"username": ADMIN_STAFF_USERNAME, "password": ADMIN_PASSWORD}
    )
    return response.json()["access"]


@pytest.fixture
def editor_token(api_client, editor_user):
    """Fixture que retorna um token JWT para o usuário editor"""
    url = "/api/v1/auth/token/"
    response = api_client.post(
        url, {"username": EDITOR_USERNAME, "password": EDITOR_PASSWORD}
    )
    return response.json()["access"]


@pytest.fixture
def reader_token(api_client, reader_user):
    """Fixture que retorna um token JWT para o usuário leitor"""
    url = "/api/v1/auth/token/"
    response = api_client.post(
        url, {"username": READER_USERNAME, "password": READER_PASSWORD}
    )
    return response.json()["access"]
