from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, UpdateView

from blog.forms import CommentForm, ProfileForm
from blog.mixins import AuthorRequiredMixin, PostMixin
from blog.models import Category, Comment, Post
from blog.utils import get_paginated_page


User = get_user_model()

LIMIT_POSTS = getattr(settings, 'LIMIT_POSTS', 10)


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    current_time = timezone.now()

    posts = user.posts.filter(
        Q(author__username=username) | Q(author=user) & Q(
            is_published=True) & Q(
            category__is_published=True) & Q(
                pub_date__lte=current_time)
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    return render(
        request,
        'blog/profile.html', {
            'profile': user,
            'page_obj': get_paginated_page(request, posts, LIMIT_POSTS)
        }
    )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:edit_profile',
            kwargs={'username': self.request.user.username})


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(
    LoginRequiredMixin,
    AuthorRequiredMixin,
    PostMixin,
    UpdateView
):
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


@login_required
def delete_post(request, post_id):
    delete_post = get_object_or_404(Post, pk=post_id, author=request.user)
    if request.method == 'POST':
        delete_post.delete()
        return redirect('blog:profile', request.user)
    return render(
        request,
        'blog/create.html', {
            'post': delete_post, 'is_delete': True
        }
    )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = super().get_object()

        if (
            self.request.user != post.author
            and (
                not post.is_published
                or not post.category.is_published
                or post.pub_date > timezone.now()
            )
        ):
            raise Http404('Страница не найдена')

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


def index(request):
    posts = Post.published.all().annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    return render(request, 'blog/index.html', {
        'page_obj': get_paginated_page(request, posts, LIMIT_POSTS)
    })


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = category.posts(manager='published').all()

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': get_paginated_page(request, post_list, LIMIT_POSTS)
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', post_id)

    return render(request, 'blog/detail.html', {
        'form': form,
        'post': post,
        'comments': post.comments.select_related('author')
    })


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if comment.author != request.user:
        raise Http404('Страница не найдена')

    form = CommentForm(request.POST or None, instance=comment)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
        'is_edit': True
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', {
        'comment': comment,
        'is_delete': True
    })
