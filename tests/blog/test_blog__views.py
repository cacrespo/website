from http import HTTPStatus
from django.test import TestCase
from django.contrib.auth import get_user_model
from blog.models import Post, Category, Article
from django.utils import timezone

User = get_user_model()


class BlogViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # Create test category
        self.category = Category.objects.create(name="Test Category")

        # Create test post
        self.post = Post.objects.create(
            author=self.user,
            title="Test Post",
            slug="test-post",
            text="Test content",
            status=1,  # Published
            published_at=timezone.now(),
        )
        self.post.categories.add(self.category)

        # Create test article
        self.article = Article.objects.create(
            title="Test Article",
            author="Test Author",
            comment="Test comment",
            link="https://example.com",
        )

    def test_blog_list_view(self):
        response = self.client.get("/blog/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "blog/base.html")
        self.assertIn("posts", response.context)
        self.assertEqual(len(response.context["posts"]), 1)
        self.assertEqual(response.context["posts"][0], self.post)

    def test_blog_category_view(self):
        response = self.client.get(f"/blog/category/{self.category.name}/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "blog/base.html")
        self.assertIn("posts", response.context)
        self.assertIn("category", response.context)
        self.assertEqual(response.context["category"], self.category.name)
        self.assertEqual(len(response.context["posts"]), 1)
        self.assertEqual(response.context["posts"][0], self.post)

    def test_blog_post_view(self):
        response = self.client.get(f"/blog/post/{self.post.pk}/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "blog/post.html")
        self.assertIn("post", response.context)
        self.assertEqual(response.context["post"], self.post)

    def test_blog_article_view(self):
        response = self.client.get("/blog/article/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "blog/article.html")
        self.assertIn("articles", response.context)
        self.assertEqual(len(response.context["articles"]), 1)
        self.assertEqual(response.context["articles"][0], self.article)

    def test_blog_post_view_invalid_pk(self):
        response = self.client.get("/blog/post/999/")  # Non-existent post
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_blog_category_view_no_posts(self):
        response = self.client.get("/blog/category/non-existent/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "blog/base.html")
        self.assertEqual(len(response.context["posts"]), 0)
