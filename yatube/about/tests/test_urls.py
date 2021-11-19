# posts/tests/test_urls.py
from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import User
from yatube.settings import HTML_S

URL_AUTHOR = '/about/author/'
URL_TECH = '/about/tech/'
USER = 'user_a'

FOR_GUEST_TEST = {
    URL_TECH: HTTPStatus.OK,
    URL_AUTHOR: HTTPStatus.OK,
}
URL_ADRESS = {
    URL_AUTHOR: HTML_S['h_author'],
    URL_TECH: HTML_S['h_tech'],
}


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username=USER)

    def setUp(self):
        self.guest_client = Client()

    def test_url_quest_about(self):
        """Страницы доступные гостю About."""
        for page_url, resp_code in FOR_GUEST_TEST.items():
            with self.subTest(page_url=page_url):
                resp = self.guest_client.get(page_url)
                self.assertEqual(resp.status_code, resp_code, page_url)

    def test_url_adress_about(self):
        """Страница соответствие URL HTTP About."""
        for adress, template in URL_ADRESS.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
