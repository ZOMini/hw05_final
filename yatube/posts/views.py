from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from core.time_func import timeit
from yatube.settings import HTML_S, YATUBE_CONST

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@timeit
def index(request):
    template = HTML_S['h_index']
    text = 'Это главная страница проекта Yatube'
    posts = Post.objects.select_related('group', 'author').all()
    paginator = Paginator(posts, YATUBE_CONST['count_pag'])
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'posts': posts,
        'text': text,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@timeit
def group_posts(request, slug):
    template = HTML_S['h_group']
    text = 'Здесь будет информация о группах проекта Yatube'
    paginator = Paginator(
        Group.objects.get(slug=slug).group_posts.all()
        .select_related('author'), YATUBE_CONST['count_pag'])
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'text': text,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@timeit
def profile(request, username):
    template = HTML_S['h_profile']
    author = User.objects.get(username=username)
    posts = author.posts.all().select_related('group', 'author',)
    paginator = Paginator(posts, YATUBE_CONST['count_pag'])
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    try:
        following = Follow.objects.get(user=request.user, author=author)
    except Exception:
        following = False
    context = {
        'following': following,
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@timeit
def post_detail(request, post_id):
    template = HTML_S['h_post']
    form = CommentForm(request.POST or None)
    post = Post.objects.select_related('group', 'author').get(id=post_id)
    comments = post.comments.all()
    context = {
        'form': form,
        'comments': comments,
        'post': post,
    }
    return render(request, template, context)


@timeit
@login_required
def post_create(request):
    template = HTML_S['h_edit_create']
    form = PostForm(request.POST, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, template, {'form': form})


@timeit
@login_required
def post_edit(request, post_id):
    template = HTML_S['h_edit_create']
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        post.save(force_update=True)
        return redirect('posts:post_detail', post_id=post.id)
    return render(
        request, template, {'form': form, 'is_edit': is_edit, 'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, YATUBE_CONST['count_pag'])
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author_follow = get_object_or_404(User, username=username)
    if author_follow != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author_follow
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    follow = Follow.objects.filter(
        author__username=username, user=request.user)
    follow.delete()
    return redirect('posts:profile', username=username)
