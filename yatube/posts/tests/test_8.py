from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()
SLUG_1 = '1'
SLUG_2 = '2'
GROUP_1 = reverse('posts:group_list', kwargs={'slug': SLUG_1})
GROUP_2 = reverse('posts:group_list', kwargs={'slug': SLUG_2})


class Testsubunsub(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_a = User.objects.create_user(username="user_a")
        cls.author_p = User.objects.create_user(username="author_p")
        cls.group = Group.objects.create(
            slug=SLUG_1,
            title="test-title",
            description="test-desc",
        )

    def setUp(self):
        self.author = User.objects.create(
            username="test_name",
        )
        self.post = Post.objects.create(
            author=self.author,
            text="Текст, написанный для проверки",
            group=self.group,
        )
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_user_unsub_and_sub_2(self):
        user2 = User.objects.create_user(username='User2')
        Follow.objects.create(user=self.author_p, author=user2)
        followers_count = Follow.objects.filter(
            user=self.author_p, author=user2).count()
        self.assertEqual(followers_count, 1)
        self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': user2}))
        followers_count = Follow.objects.filter(
            user=self.user_a, author=user2).count()
        self.assertEqual(followers_count, 0)

    def test_follow_post_exists_in_follow_index_2(self):
        user2 = User.objects.create_user(username='User2')
        post = Post.objects.create(text='Проверка подписки',
                                   author=self.author)
        Follow.objects.create(user=user2, author=self.author)
        authorized_client = Client()
        authorized_client.force_login(user2)
        response = authorized_client.get(reverse('posts:follow_index'))
        post_text1 = response.context['page_obj'][0].text
        self.assertEqual(post.text, post_text1)
