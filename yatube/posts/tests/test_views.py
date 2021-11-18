import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post, User
from yatube.settings import HTML_S, YATUBE_CONST

PAGE = YATUBE_CONST['count_pag']
SLUG_1 = 'test-slug'
SLUG_2 = 'group-2'
USER = 'user_a'
AUTHOR = 'author_p'
POST_NUM = '1'
TITLE = 'Тестовая группа'
DESCRIPTION = 'Тестовое описание'
TEXT1 = 'Тестовый текст'

INDEX_NAME = 'posts:index'
GROUP_LIST_NAME = 'posts:group_list'
PROFILE_NAME = 'posts:profile'
POST_DETAIL_NAME = 'posts:post_detail'
POST_EDIT_NAME = 'posts:post_edit'
CREATE_NAME = 'posts:post_create'
SIGNUP_NAME = 'users:signup'
FOLLOW_NAME = 'posts:follow_index'

INDEX = reverse(INDEX_NAME)
GROUP_1 = reverse(GROUP_LIST_NAME, kwargs={'slug': SLUG_1})
GROUP_2 = reverse(GROUP_LIST_NAME, kwargs={'slug': SLUG_2})
PROFILE_USER = reverse(PROFILE_NAME, kwargs={'username': USER})
PROFILE_AUTHOR = reverse(PROFILE_NAME, kwargs={'username': AUTHOR})
POST_DETAIL = reverse(POST_DETAIL_NAME, kwargs={'post_id': POST_NUM})
POST_EDIT = reverse(POST_EDIT_NAME, kwargs={'post_id': POST_NUM})
CREATE = reverse(CREATE_NAME)
SIGNUP = reverse(SIGNUP_NAME)
FOLLOW = reverse(FOLLOW_NAME)

TEMP_PAGE_NAMES = {
    INDEX: HTML_S['h_index'],
    GROUP_1: HTML_S['h_group'],
    PROFILE_USER: HTML_S['h_profile'],
    POST_DETAIL: HTML_S['h_post'],
    POST_EDIT: HTML_S['h_edit_create'],
    CREATE: HTML_S['h_edit_create'],
    SIGNUP: HTML_S['h_signup'],
}
FORM_FIELDS = {
    'text': forms.fields.CharField,
    'group': forms.models.ModelChoiceField,
    'image': forms.fields.ImageField,
}
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED_GIF = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class AllViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username=USER)
        cls.author_p = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title=TITLE,
            description=DESCRIPTION,)
        cls.post = Post.objects.create(
            author=cls.author_p,
            text=TEXT1,
            group=cls.group,
            image=UPLOADED_GIF)
        time.sleep(0.01)  # Иначе сортирует не верно.
        Post.objects.create(author=cls.author_p,
                            text='text_2',
                            image=UPLOADED_GIF
                            )
        for i in range(13):
            time.sleep(0.01)  # Без этого тесты ломаются.
            Post.objects.create(author=cls.user_a,
                                text=f'text{i}',
                                group=cls.group,
                                image=UPLOADED_GIF
                                )
        # Если сделать через bulk_create, как ниже, или убрать sleep, как выше,
        # то посты создаются в случайном порядке, видимо pub_date
        # (= случайные ID) одинаковый, ну соответственно все тесты ниже
        # ломаются, но это не точно :), готов осознать свою ошибку:).

        # posts = (
        #     Post(text=f'text{i}', author=cls.user_a,
        #          group=cls.group) for i in range(13)
        # )
        # Post.objects.bulk_create(posts, 13)
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()    
    
    def setUp(self):
        self.guest_client = Client()
        self.a_c_author = Client()
        self.a_c_author.force_login(self.author_p)

    def test_pages_uses_correct_template(self):
        for reverse_name, template in TEMP_PAGE_NAMES.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.a_c_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем пэджинатор.
    def test_index_first_page(self):
        # индекс 1-я стр, 10
        response = self.a_c_author.get(INDEX)
        self.assertEqual(len(response.context['page_obj']), PAGE)

    def test_index_second_page(self):
        # индек 2-я стр, 5 постов
        response = self.a_c_author.get(INDEX + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_group_posts_first_page(self):
        # гроуп 1-я = 10
        response = self.a_c_author.get(GROUP_1)
        self.assertEqual(len(response.context['page_obj']), PAGE)

    def test_group_posts_second_page(self):
        # 2-я стр. группы = 4 поста
        response = self.a_c_author.get(GROUP_1 + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_profile_first_page(self):
        # профайл 1-я 10
        response = self.a_c_author.get(PROFILE_USER)
        self.assertEqual(len(response.context['page_obj']), PAGE)

    def test_profile_second_page(self):
        # профайл 2-я 3
        response = self.a_c_author.get(PROFILE_USER + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    # Проверяем контекст страниц.
    def test_index_pages(self):
        response = self.a_c_author.get(INDEX)
        obj = response.context['page_obj'][1]
        self.assertEqual(obj.author, self.user_a)
        self.assertEqual(obj.text, 'text11')
        self.assertTrue(obj.image)

    def test_post_create_page(self):
        response = self.a_c_author.get(CREATE)
        for value, expected in FORM_FIELDS.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_pages(self):
        response = self.a_c_author.get(POST_DETAIL)
        self.assertEqual(response.context.get('post').text, TEXT1)
        self.assertEqual(response.context.get('post').author,
                         self.author_p)
        self.assertEqual(response.context.get('post').group,
                         self.group)
        self.assertTrue(response.context.get('post').image)

    def test_post_detail_comment(self):
        """Авторизованный пользователь может писать комментарии"""
        comments_count = Comment.objects.count()
        new_comment = (Comment.objects.create(
            post=self.post,
            author=self.user_a, text='коммент 1')).text
        resp = self.a_c_author.get(POST_DETAIL)
        comment_2 = resp.context['comments'][0].text
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        # Коммент добавился.
        self.assertEqual(comment_2, new_comment)
        # Коммент совпадает.

    def test_group_posts_pages(self):
        response = self.a_c_author.get(GROUP_1)
        obj = response.context['page_obj'][0]
        self.assertEqual(obj.text, 'text12')
        self.assertEqual(obj.author, self.user_a)
        self.assertEqual(obj.group, self.group)
        self.assertTrue(obj.image)

    def test_profile_pages(self):
        response = self.a_c_author.get(PROFILE_AUTHOR)
        user = User.objects.get(username=AUTHOR)
        obj = response.context['page_obj'][0]
        self.assertEqual(obj.text, 'text_2')
        self.assertEqual(obj.author, user)
        self.assertTrue(obj.image)

    # Проверяем последний созданный пост с группой.

    def test_last_post_in_group(self):
        """ В группах 1-й пост должен быть последним из созданных.
         И в своей ли он группе."""
        response = self.a_c_author.get(GROUP_1)
        self.assertEqual(response.context['page_obj'][0].id, 15)
        self.assertEqual(response.context['page_obj'][0].group, self.group)

    def test_last_post_in_index(self):
        """ В индексе 1-й пост должен быть последним из созданных.
         Группа в норме."""
        response = self.a_c_author.get(INDEX)
        self.assertEqual(response.context['page_obj'][0].id, 15)
        self.assertEqual(response.context['page_obj'][0].group, self.group)

    def test_last_post_in_profile(self):
        """ В профайле 1-й пост должен быть последним из созданных.
         Группа в норме."""
        response = self.a_c_author.get(PROFILE_USER)
        self.assertEqual(response.context['page_obj'][0].id, 15)
        self.assertEqual(response.context['page_obj'][0].group, self.group)

    def test_post_in_2_group(self):
        """ Проверяем не отображается ли пост, принадлежащий
         "2"-й группе, в "1"-й."""
        g2 = Group.objects.create(slug=SLUG_2, title='Тестовая группа2',
                                  description='Тестовое описание2',)
        Post.objects.create(author=self.author_p, text='text_16', group=g2)
        response = self.a_c_author.get(GROUP_1)
        self.assertEqual(response.context['page_obj'][0].id, 15)
        """ Так-как 15-й пост остался 1-м в группе "1", значит 16-й пост,
         из группы "2", не отображается в "1"-й группе - Ок."""

    def test_index_cache(self):
        """Тест index кэш."""
        Post.objects.all().delete()
        self.a_c_author.post(INDEX, {'text': 'Тестовый пост1!'}, follow=True)
        response = self.a_c_author.get(INDEX)
        content = response.content
        Post.objects.all().delete()
        # time.sleep(21)  # Проверяем ломается ли тест.
        response = self.a_c_author.get(INDEX)
        self.assertEqual(content, response.content)
        cache.clear()
        response = self.a_c_author.get(INDEX)
        self.assertNotEqual(content, response.content)

    def test_user_unsub_and_sub(self):
        user2 = User.objects.create_user(username='User2')
        Follow.objects.create(user=self.author_p, author=user2)
        followers_count = Follow.objects.filter(
            user=self.author_p, author=user2).count()
        self.assertEqual(followers_count, 1)
        self.guest_client.get(reverse(
            PROFILE_NAME, kwargs={'username': user2}))
        followers_count = Follow.objects.filter(
            user=self.user_a, author=user2).count()
        self.assertEqual(followers_count, 0)

    def test_follow_post_exists_in_follow_index(self):
        user2 = User.objects.create_user(username='User2')
        post = Post.objects.create(text='Проверка подписки', author=user2)
        Follow.objects.create(user=self.author_p, author=user2)
        response = self.a_c_author.get(FOLLOW)
        post_text1 = response.context['page_obj'][0].text
        self.assertEqual(post.text, post_text1)

    def test_unfollow_post_does_not_exists_in_follow_index(self):
        user2 = User.objects.create_user(username='User2')
        post = Post.objects.create(text='Проверка подписки', author=user2)
        test_client = Client()
        test_client.force_login(user2)
        Follow.objects.create(user=user2, author=self.author_p)
        response = test_client.get(FOLLOW)
        post_text1 = response.context['page_obj'][0].text
        self.assertNotEqual(post.text, post_text1)

