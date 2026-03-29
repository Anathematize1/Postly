from datetime import datetime

from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .forms import ProfileEditForm, CreatePostForm, CommentForm
from .models import Post, Category, Comment


User = get_user_model()

POSTS_PER_PAGE = 10


def paginate(request, queryset):
    """Разбивает queryset на страницы."""
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def get_queryset_posts():
    """Возвращает отсортированные посты."""
    return (
        Post.objects.select_related('category', 'author', 'location')
        .annotate(comment_count=Count('comments'))
        .filter(
            pub_date__lte=datetime.now(),
            is_published=True,
            category__is_published=True
        )
        .order_by('-pub_date')
    )


def profile(request, username):
    """Отображает страницу профиля пользователя."""
    profile = get_object_or_404(User, username=username)

    if request.user == profile:
        user_posts = Post.objects.annotate(
            comment_count=Count('comments')
        ).filter(author=profile
                 ).order_by('-pub_date')
    else:
        user_posts = get_queryset_posts().filter(author=profile)

    page_obj = paginate(request, user_posts)
    context = {
        'profile': profile,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    """Отображает страницу редактирования профиля"""
    user = request.user
    form = ProfileEditForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', user.username)
    context = {'form': form}

    return render(request, 'blog/user.html', context)


@login_required
def create_post(request):
    """Отображает страницу создания публикации."""
    form = CreatePostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def edit_post(request, post_id):
    """Отображает страницу редактирования публикации пользователя."""
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id)

    form = CreatePostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'blog/create.html', context)


def delete_post(request, post_id):
    """Отображает страницу удаления публикации пользователя"""
    user = request.user
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', post_id)

    form = CreatePostForm(instance=post)
    context = {'form': form}

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', user.username)

    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    """Добавляет комментарий к публикации."""
    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

        return redirect('blog:post_detail', post_id)


def edit_comment(request, post_id, comment_id):
    """Редактирует комментарий пользователя."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', post_id)

    form = CommentForm(
        request.POST or None,
        instance=comment
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {
        'form': form,
        'comment': comment,
    }
    return render(request, 'blog/comment.html', context)


def delete_comment(request, post_id, comment_id):
    """Удаляет комментарий пользователя."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    context = {'comment': comment}
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', context)


def index(request):
    """Отображает главную страницу со списком публикаций."""
    post_list = get_queryset_posts()
    page_obj = paginate(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Отображает страницу отдельной публикации."""
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        post = get_object_or_404(get_queryset_posts(), pk=post_id)

    form = CommentForm()
    comments = post.comments.filter(
        is_published=True
    )
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Отображает страницу с постами в отдельной категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = get_queryset_posts().filter(category=category)
    page_obj = paginate(request, post_list)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)
