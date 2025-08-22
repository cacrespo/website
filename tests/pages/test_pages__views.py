from http import HTTPStatus
from django.test import SimpleTestCase, TestCase
from blog.models import Activity


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


class ContactViewTests(SimpleTestCase):
    def test_get(self):
        response = self.client.get("/contact/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "pages/contact.html")


# class AboutViewTests(SimpleTestCase):
#    def test_get(self):
#        response = self.client.get("/about/")
#
#        self.assertEqual(response.status_code, HTTPStatus.OK)
#        self.assertTemplateUsed(response, "pages/about.html")
