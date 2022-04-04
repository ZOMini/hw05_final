import time

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()
SLUG_1 = '1'
SLUG_2 = '2'
GROUP_1 = reverse('posts:group_list', kwargs={'slug': SLUG_1})
GROUP_2 = reverse('posts:group_list', kwargs={'slug': SLUG_2})


class TaskViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username='test_username_a')
        cls.author_p = User.objects.create_user(username='test_author_p')
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title='test-title',
            description='test-description',
        )

    def setUp(self):
        self.author = User.objects.create(
            username='test_username',
        )
        self.post = Post.objects.create(
            author=self.author,
            text='тестовый текс,ЭЪ/!"№;%:?*()_',
            group=self.group,
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class TaskPaginatorsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username='test_username_a')
        cls.author_p = User.objects.create_user(username='test_author_p')
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title='test-title',
            description='test-description',
        )
        cls.posts = (Post(text=f'text{i}', author=cls.user_a,
                     group=cls.group) for i in range(13))
        Post.objects.bulk_create(cls.posts, 13)
        cls.TEMP = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': cls.user_a.username}
            )
        )

    def setUp(self):
        self.guest_client = Client()

    def test_item_posts_per_page(self):
        for page_name in self.TEMP:
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(page_name)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.guest_client.get(page_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class AnotherTests(TestCase):
    def setUp(self):
        self.author_p = User.objects.create_user(username='test_author_p')
        self.group_1 = Group.objects.create(
            slug=1, title='testtitle1', description='testdesc1'
        )
        self.group_2 = Group.objects.create(
            slug=2, title='testtitle2', description='testdesc2'
        )
        self.post2 = Post.objects.create(
            author=self.author_p, text='text_2', group=self.group_2)
        time.sleep(0.01)  # Иначе посты имеют случайный порядок.
        self.post1 = Post.objects.create(
            author=self.author_p, text='text_1', group=self.group_1)
        self.guest_client = Client()
        self.a_c_author = Client()
        self.a_c_author.force_login(self.author_p)

    def test_post_in_2_group_2(self):
        response = self.a_c_author.get(GROUP_1)
        self.assertEqual(response.context['page_obj'][0].group.id,
                         self.group_1.slug)
        self.assertEqual(response.context['page_obj'][0].text,
                         self.post1.text)
        response = self.a_c_author.get(GROUP_2)
        self.assertEqual(response.context['page_obj'][0].group.id,
                         self.group_2.slug)
        self.assertEqual(response.context['page_obj'][0].text, self.post2.text)

    def test_index_correct_context(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.context['page_obj'].paginator.count, 2)
        self.assertEqual(response.context['page_obj'][0].text,
                         self.post1.text)
        self.assertEqual(response.context['page_obj'][0].author,
                         self.post1.author)
        self.assertEqual(response.context['page_obj'][0].group,
                         self.post1.group)
        self.assertEqual(response.context['page_obj'][1].text, self.post2.text)

    def test_group_list_correct_context(self):
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_1.slug})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group, self.group_1)
        self.assertEqual(response.context['page_obj'][0].text, self.post1.text)

    def test_profile_correct_context(self):
        response = self.guest_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.author_p.username})
        )
        self.assertEqual(response.context['page_obj'][0].author, self.author_p)
        self.assertEqual(response.context['page_obj'][0].text, self.post1.text)
        self.assertEqual(response.context['page_obj'][1].text, self.post2.text)

    def test_create_post_2(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'тест текст',
            'group': self.group_1.id
        }
        response = self.a_c_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author_p})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        latest_post = Post.objects.first()
        self.assertEqual(latest_post.text, form_data['text'])
        self.assertEqual(latest_post.author, self.author_p)
        self.assertEqual(latest_post.group.id, form_data['group'])

    def test_post_edit_2(self):
        post_edit = Post.objects.create(
            author=self.author_p,
            text='тест текст',
        )
        form_data = {
            'text': 'измененный текст',
        }
        response = self.a_c_author.post(
            reverse('posts:post_edit', kwargs={'post_id': post_edit.id}),
            data=form_data,
            follow=True,
        )
        post_edit.refresh_from_db()
        self.assertEqual(post_edit.text, form_data['text'])
        self.assertEqual(post_edit.author, self.author_p)
        self.assertIsInstance(response.context.get('form').fields.get('text'),
                              forms.fields.CharField)
