from unittest.mock import MagicMock, patch

import httpx
from django.contrib.auth.models import User
from django.urls import reverse
from pydantic_ai.models.test import TestModel
from rest_framework import status
from rest_framework.test import APITestCase

from blog.extractor import article_agent
from blog.models import Article


class ArticleAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.article_data = {
            "title": "Test Article",
            "author": "Test Author",
            "comment": "This is a test comment.",
            "link": "http://example.com",
        }
        self.article = Article.objects.create(**self.article_data)
        self.url = reverse("api-article-list-create")

    def test_list_articles(self):
        """
        Ensure we can retrieve a list of articles.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], self.article_data["title"])

    def test_create_article_authenticated(self):
        """
        Ensure we can create a new article as an authenticated user.
        """
        self.client.login(username="testuser", password="testpassword")
        new_article_data = {
            "title": "New Article",
            "author": "New Author",
            "comment": "Another test comment.",
            "link": "http://newexample.com",
        }
        response = self.client.post(self.url, new_article_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(Article.objects.last().title, new_article_data["title"])

    def test_create_article_unauthenticated(self):
        """
        Ensure we cannot create a new article as an unauthenticated user.
        """
        new_article_data = {
            "title": "Unauthorized Article",
            "author": "Unauthorized Author",
            "comment": "This should not be created.",
            "link": "http://unauthorized.com",
        }
        response = self.client.post(self.url, new_article_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            Article.objects.count(), 1
        )  # Should still be only the initial article

    def test_create_article_invalid_data(self):
        """
        Ensure we cannot create an article with invalid data.
        """
        self.client.login(username="testuser", password="testpassword")
        invalid_article_data = {
            "title": "",  # Invalid: title cannot be empty
            "author": "Invalid Author",
            "comment": "This should fail.",
            "link": "invalid-link",  # Invalid URL
        }
        response = self.client.post(self.url, invalid_article_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertIn("link", response.data)
        self.assertEqual(Article.objects.count(), 1)

    def test_auto_create_article_unauthenticated(self):
        """
        Ensure unauthenticated requests to auto-create are rejected.
        """
        auto_url = reverse("api-article-auto-create")
        response = self.client.post(
            auto_url, {"url": "https://example.com/article"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Article.objects.count(), 1)

    def test_auto_create_article_invalid_url(self):
        """
        Ensure invalid URLs return 400 Bad Request.
        """
        self.client.login(username="testuser", password="testpassword")
        auto_url = reverse("api-article-auto-create")
        response = self.client.post(auto_url, {"url": "not-a-valid-url"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("url", response.data)
        self.assertEqual(Article.objects.count(), 1)

    @patch("blog.extractor.httpx.Client")
    def test_auto_create_article_success(self, mock_client_cls):
        """
        Ensure an article is automatically created from URL using LLM extraction.
        """
        self.client.login(username="testuser", password="testpassword")
        auto_url = reverse("api-article-auto-create")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head>
                <title>Exciting AI Breakthrough</title>
                <meta name="author" content="Alice Smith">
                <meta name="description" content="A breakthrough in neural networks.">
            </head>
            <body>
                <article>
                    <h1>Exciting AI Breakthrough</h1>
                    <p>Details about the breakthrough in AI.</p>
                </article>
            </body>
        </html>
        """
        mock_response.raise_for_status.return_value = None
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        test_model = TestModel(
            custom_output_args={
                "title": "Exciting AI Breakthrough",
                "author": "Alice Smith",
                "description": "A breakthrough in neural networks.",
            }
        )

        with article_agent.override(model=test_model):
            response = self.client.post(
                auto_url,
                {"url": "https://example.com/ai-article"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Exciting AI Breakthrough")
        self.assertEqual(response.data["author"], "Alice Smith")
        self.assertEqual(response.data["comment"], "A breakthrough in neural networks.")
        self.assertEqual(response.data["link"], "https://example.com/ai-article")
        self.assertEqual(Article.objects.count(), 2)

        created_article = Article.objects.get(link="https://example.com/ai-article")
        self.assertEqual(created_article.title, "Exciting AI Breakthrough")
        self.assertIsNotNone(created_article.embedding)

    @patch("blog.extractor.httpx.Client")
    def test_auto_create_article_comment_override(self, mock_client_cls):
        """
        Ensure user comment overrides the extracted description when provided.
        """
        self.client.login(username="testuser", password="testpassword")
        auto_url = reverse("api-article-auto-create")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><article>Some content</article></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        test_model = TestModel(
            custom_output_args={
                "title": "Extracted Title",
                "author": "Extracted Author",
                "description": "Extracted description that should be overridden.",
            }
        )

        with article_agent.override(model=test_model):
            response = self.client.post(
                auto_url,
                {
                    "url": "https://example.com/override-article",
                    "comment": "My personal reading notes.",
                },
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["comment"], "My personal reading notes.")
        created_article = Article.objects.get(
            link="https://example.com/override-article"
        )
        self.assertEqual(created_article.comment, "My personal reading notes.")

    @patch("blog.extractor.httpx.Client")
    def test_auto_create_article_fetch_http_error(self, mock_client_cls):
        """
        Ensure HTTP errors when fetching the URL return 400 Bad Request.
        """
        self.client.login(username="testuser", password="testpassword")
        auto_url = reverse("api-article-auto-create")

        mock_request = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get.side_effect = httpx.HTTPStatusError(
            "Not Found", request=mock_request, response=mock_response
        )
        mock_client_cls.return_value = mock_client

        response = self.client.post(
            auto_url,
            {"url": "https://example.com/non-existent"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(Article.objects.count(), 1)

    def test_extract_article_unauthenticated(self):
        """
        Ensure unauthenticated requests to extract endpoint are rejected.
        """
        extract_url = reverse("api-article-extract")
        response = self.client.post(
            extract_url, {"url": "https://example.com/article"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extract_article_invalid_url(self):
        """
        Ensure invalid URLs to extract endpoint return 400 Bad Request.
        """
        self.client.login(username="testuser", password="testpassword")
        extract_url = reverse("api-article-extract")
        response = self.client.post(
            extract_url, {"url": "not-a-valid-url"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("url", response.data)

    @patch("blog.extractor.httpx.Client")
    def test_extract_article_success(self, mock_client_cls):
        """
        Ensure extract endpoint returns extracted fields without saving to DB.
        """
        self.client.login(username="testuser", password="testpassword")
        extract_url = reverse("api-article-extract")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><h1>Article</h1></body></html>"
        mock_response.raise_for_status.return_value = None
        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        test_model = TestModel(
            custom_output_args={
                "title": "Extracted Preview Title",
                "author": "John Doe",
                "description": "Preview description for admin review.",
            }
        )

        initial_count = Article.objects.count()
        with article_agent.override(model=test_model):
            response = self.client.post(
                extract_url,
                {"url": "https://example.com/preview"},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Extracted Preview Title")
        self.assertEqual(response.data["author"], "John Doe")
        self.assertEqual(
            response.data["description"], "Preview description for admin review."
        )
        # Ensure it was NOT saved to database (human in the loop review)
        self.assertEqual(Article.objects.count(), initial_count)
