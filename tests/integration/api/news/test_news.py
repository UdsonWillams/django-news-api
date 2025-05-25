import pytest
from rest_framework import status
from rest_framework.test import APIClient

from news.models import News

# Constantes de URL
BASE_URL = "/api/v1/news/articles/"


def get_detail_url(article_id):
    """Helper para criar URLs de detalhe de artigos"""
    return f"{BASE_URL}{article_id}/"


@pytest.mark.django_db
class TestNewsAPI:
    def test_list_published_news_anonymous(
        self,
        api_client: APIClient,
        reader_token,
        published_news: News,
        unpublished_news: News,
    ):
        """Testa se usuários anônimos podem listar notícias publicadas"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")
        response = api_client.get(BASE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

        assert response.data["results"][0]["id"] == published_news.id
        assert (
            response.data["results"][0]["is_published"] == published_news.is_published
        )

    def test_list_news_with_admin(
        self,
        api_client: APIClient,
        admin_token: str,
        published_news: News,
        unpublished_news: News,
    ):
        """Testa se administradores podem ver todas as notícias, incluindo não publicadas"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        response = api_client.get(BASE_URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        # Published news
        assert response.data["results"][0]["id"] == published_news.id
        assert (
            response.data["results"][0]["is_published"] == published_news.is_published
        )

        # Unpublished news
        assert response.data["results"][1]["id"] == unpublished_news.id
        assert (
            response.data["results"][1]["is_published"] == unpublished_news.is_published
        )

    def test_create_news_editor(self, api_client: APIClient, editor_token, vertical):
        """Testa se editores podem criar notícias"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {editor_token}")

        data = {
            "title": "Nova Notícia de Teste",
            "content": "Conteúdo da notícia de teste",
            "category": "poder",
            "verticals": [vertical.id],
            "status": News.StatusChoices.DRAFT,
        }

        response = api_client.post(BASE_URL, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert News.objects.filter(title="Nova Notícia de Teste").exists()

    def test_create_news_reader_forbidden(self, api_client: APIClient, reader_token):
        """Testa se leitores não podem criar notícias"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {reader_token}")

        data = {
            "title": "Tentativa de Notícia",
            "content": "Conteúdo não permitido",
            "category": "poder",
        }

        response = api_client.post(BASE_URL, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_news_author(
        self, api_client: APIClient, editor_token, published_news
    ):
        """Testa se o autor pode atualizar sua própria notícia"""
        # Assume que published_news foi criado pelo editor_user
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {editor_token}")
        url = get_detail_url(published_news.id)

        data = {"title": "Título Atualizado"}

        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        published_news.refresh_from_db()
        assert published_news.title == "Título Atualizado"

    def test_update_news_admin(
        self, api_client: APIClient, admin_token, published_news
    ):
        """Testa se um admin pode atualizar qualquer notícia"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = get_detail_url(published_news.id)

        data = {"title": "Título Alterado pelo Admin"}

        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        published_news.refresh_from_db()
        assert published_news.title == "Título Alterado pelo Admin"

    def test_delete_news_admin(
        self, api_client: APIClient, admin_token, published_news
    ):
        """Testa se um admin pode excluir notícias"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = get_detail_url(published_news.id)

        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not News.objects.filter(id=published_news.id).exists()

    def test_filter_news_by_category(
        self, api_client: APIClient, admin_token: str, published_news: News
    ):
        """Testa se notícias podem ser filtradas por categoria específica"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = f"{BASE_URL}?category={published_news.category}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) > 0

    def test_filter_news_by_author(
        self, api_client: APIClient, admin_token: str, published_news: News
    ):
        """Testa se notícias podem ser filtradas pelo ID do autor"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = f"{BASE_URL}?author={published_news.author.id}"
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) > 0

    def test_search_news(
        self, api_client: APIClient, admin_token: str, published_news: News
    ):
        """Testa se a funcionalidade de busca retorna notícias por termo parcial do título"""
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_token}")
        url = f"{BASE_URL}?search={published_news.title[:5]}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) > 0
