from http import HTTPStatus
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from blog.models import Activity
from pages.forms import ContactForm


class FaviconTests(TestCase):
    def test_get(self):
        response = self.client.get("/favicon.ico")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["Cache-Control"], "max-age=86400, immutable, public")
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertGreater(len(response.getvalue()), 0)


class HomeViewTests(TestCase):
    def setUp(self):
        # Create test activities
        self.activity1 = Activity.objects.create(
            details="Test Activity 1", link="https://example.com/1", link_hpv="Link 1"
        )
        self.activity2 = Activity.objects.create(
            details="Test Activity 2", link="https://example.com/2", link_hpv="Link 2"
        )
        self.activity3 = Activity.objects.create(
            details="Test Activity 3", link="https://example.com/3", link_hpv="Link 3"
        )

    def test_get(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "pages/home.html")
        self.assertIn("activities", response.context)
        self.assertEqual(len(response.context["activities"]), 3)


class ContactViewTests(TestCase):
    def test_get(self):
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "pages/contact.html")
        self.assertIsInstance(response.context["form"], ContactForm)

    def test_post_valid_data(self):
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "This is a test message.",
            "validator": "mostaza",
        }
        response = self.client.post(reverse("contact"), data=form_data)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)  # 302 redirect
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "Contact Form submission from Test User"
        )

    def test_post_invalid_data(self):
        form_data = {
            "name": "Test User",
            "email": "",  # Invalid email
            "message": "This is a test message.",
            "validator": "mostaza",
        }
        response = self.client.post(reverse("contact"), data=form_data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn("form", response.context)
        self.assertTrue(response.context["form"].errors)

    def test_post_invalid_validator(self):
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "This is a test message.",
            "validator": "incorrecto",
        }
        response = self.client.post(reverse("contact"), data=form_data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn("form", response.context)
        self.assertIn("validator", response.context["form"].errors)

    def test_post_empty_message(self):
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "",
            "validator": "mostaza",
        }
        response = self.client.post(reverse("contact"), data=form_data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn("form", response.context)
        self.assertIn("message", response.context["form"].errors)


# class AboutViewTests(SimpleTestCase):
#    def test_get(self):
#        response = self.client.get("/about/")
#
#        self.assertEqual(response.status_code, HTTPStatus.OK)
#        self.assertTemplateUsed(response, "pages/about.html")
