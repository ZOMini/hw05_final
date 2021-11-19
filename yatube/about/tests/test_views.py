from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User
from yatube.settings import HTML_S

# Странно, но isort так и сделал импорты.
# Проверил, все ок - isort test_views.py --check-only.
# Разобрался, нужно было isort.cfg добавить/настроить.


AUTHOR_NAME = 'about:author'
TECH_NAME = 'about:tech'
AUTHOR = 'author_p'

TEMP_PAGE_NAME = {
    reverse(AUTHOR_NAME): HTML_S['h_author'],
    reverse(TECH_NAME): HTML_S['h_tech'],
}


class AboutViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_p = User.objects.create_user(username=AUTHOR)

    def setUp(self):
        self.a_c_author = Client()

    def test_pages_uses_correct_template_about(self):
        """About соответствуют ли имена и адресс."""
        for reverse_name, template in TEMP_PAGE_NAME.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.a_c_author.get(reverse_name)
                self.assertTemplateUsed(response, template)
