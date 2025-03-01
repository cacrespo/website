from http import HTTPStatus

from django.test import SimpleTestCase


class FaviconTests(SimpleTestCase):
    def test_get(self):
        response = self.client.get("/favicon.ico")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["Cache-Control"], "max-age=86400, immutable, public")
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertGreater(len(response.getvalue()), 0)


class HomeViewTests(SimpleTestCase):
    def test_get(self):
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "pages/home.html")


class ContactViewTests(SimpleTestCase):
    def test_get(self):
        response = self.client.get("/contact/")
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "pages/contact.html")


class AboutViewTests(SimpleTestCase):
    def test_get(self):
        response = self.client.get("/about/")
        
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "pages/about.html")
