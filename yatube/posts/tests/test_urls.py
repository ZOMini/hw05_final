# posts/tests/test_urls.py
from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User
from yatube.settings import HTML_S

SLUG_1 = 'test-slug'
SLUG_2 = 'group-2'
USER = 'user_a'
AUTHOR = 'author_p'
POST_NUM = '1'
TITLE = 'Тестовая группа'
DESCRIPTION = 'Тестовое описание'
TEXT1 = 'Тестовый текст'

URL_INDEX = '/'
URL_GROUP = f'/group/{SLUG_1}/'
URL_PROFILE = f'/profile/{USER}/'
URL_POST = f'/posts/{POST_NUM}/'
URL_CREATE = '/create/'
URL_EDIT = f'/posts/{POST_NUM}/edit/'
URL_SIGNUP = '/auth/signup/'
URL_LOGIN = '/auth/login/'
URL_FOLLOW = '/follow/'

FOR_GUEST_TEST = {
    URL_INDEX: HTTPStatus.OK,
    URL_GROUP: HTTPStatus.OK,
    URL_PROFILE: HTTPStatus.OK,
    URL_POST: HTTPStatus.OK,
    URL_CREATE: HTTPStatus.FOUND,
    URL_EDIT: HTTPStatus.FOUND,
    URL_SIGNUP: HTTPStatus.OK,
    URL_LOGIN: HTTPStatus.OK,
    URL_FOLLOW: HTTPStatus.FOUND,
}

URL_ADRESS = {
    URL_INDEX: HTML_S['h_index'],
    URL_GROUP: HTML_S['h_group'],
    URL_PROFILE: HTML_S['h_profile'],
    URL_POST: HTML_S['h_post'],
    URL_CREATE: HTML_S['h_edit_create'],
    URL_EDIT: HTML_S['h_edit_create'],
    URL_SIGNUP: HTML_S['h_signup'],
    URL_LOGIN: HTML_S['h_login'],
    URL_FOLLOW: HTML_S['h_follow'],
}


class AllURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username=USER)
        cls.author_p = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title=TITLE,
            description=DESCRIPTION,
        )
        cls.post = Post.objects.create(
            id='1',
            author=cls.author_p,
            text=TEXT1,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client.force_login(self.user_a)
        self.authorized_client_author.force_login(self.author_p)

    def test_url_guest(self):
        """Страницы доступные гостю."""
        for page_url, resp_code in FOR_GUEST_TEST.items():
            with self.subTest(page_url=page_url):
                resp = self.guest_client.get(page_url)
                self.assertEqual(resp.status_code, resp_code, page_url)

    def test_url_authorized(self):
        """Страницы доступные авторизованному."""
        response = self.authorized_client.get(URL_CREATE)
        self.assertTemplateUsed(response, HTML_S['h_edit_create'])
        resp = self.guest_client.get(URL_EDIT)
        self.assertEqual(resp.status_code, 302, HTML_S['h_edit_create'])

    def test_url_authorized_author(self):
        """Страницы доступные автору."""
        response = self.authorized_client_author.get(URL_EDIT)
        self.assertTemplateUsed(response, HTML_S['h_edit_create'])

    def test_url_adress(self):
        """Страницы доступные автору."""
        for adress, template in URL_ADRESS.items():
            with self.subTest(adress=adress):
                response = self.authorized_client_author.get(adress)
                self.assertTemplateUsed(response, template)
        response = self.authorized_client_author.get(URL_CREATE)
        self.assertTemplateUsed(response, HTML_S['h_edit_create'])
