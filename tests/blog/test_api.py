from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from blog.models import Article
from django.contrib.auth.models import User


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
