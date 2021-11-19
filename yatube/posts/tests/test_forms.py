from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

# Чето переборщил с констами похоже, особенно во въюхах:).

SLUG_1 = 'test-slug'
USER = 'user_a'
AUTHOR = 'author_p'
TEXT = 'text'
TEXT4 = 'text4'
TITLE = 'Тестовая группа'
DESCRIPTION = 'Тестовое описание'
TEXT1 = 'Тестовый текст'

INDEX_NAME = 'posts:index'
PROFILE_NAME = 'posts:profile'
POST_DETAIL_NAME = 'posts:post_detail'
POST_EDIT_NAME = 'posts:post_edit'
CREATE_NAME = 'posts:post_create'
SIGNUP_NAME = 'users:signup'

FORM_DATA_1 = {'text': 'Тестовый текст2'}
FORM_DATA_2 = {'text': TEXT4}
FORM_DATA_3 = {'username': AUTHOR,
               'password1': 'asqw1m2439A',
               'password2': 'asqw1m2439A'}

PROFILE_USER = reverse(PROFILE_NAME, kwargs={'username': USER})


class MyFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username=USER)
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title=TITLE,
            description=DESCRIPTION,)
        cls.post = Post.objects.create(author=cls.user_a,
                                       text=TEXT1,
                                       group=cls.group)

    def setUp(self):
        self.q_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_a)
        self.POST_DETAIL = reverse(
            POST_DETAIL_NAME, kwargs={'post_id': self.post.id})
        self.POST_EDIT = reverse(
            POST_EDIT_NAME, kwargs={'post_id': self.post.id})

    def test_form_create(self):
        """Test create form."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse(CREATE_NAME),
            data=FORM_DATA_1,
            follow=True
        )
        self.assertRedirects(response, PROFILE_USER)
        self.assertEqual(posts_count + 1, Post.objects.count())
        self.assertTrue(Post.objects.filter(text=FORM_DATA_1[TEXT]).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_form_edit_post(self):
        """Test edit post."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            self.POST_EDIT,
            data=FORM_DATA_2,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(posts_count, Post.objects.count())
        self.assertTrue(Post.objects.filter(text=TEXT4).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Разобрался, отбой.
    def test_form_signup(self):
        """Тест signup form."""
        response = self.q_client.post(reverse(SIGNUP_NAME),
                                      data=FORM_DATA_3,
                                      follow=True)
        self.assertRedirects(response, reverse(INDEX_NAME))
        self.assertTrue(User.objects.filter(username=AUTHOR).exists())
