from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.http import Http404, HttpResponseForbidden
from django.conf import settings
from blog.forms import PostForm, CommentForm, ProfileForm, PasswordChangeForm
from blog.models import Post, Category, Comment

User = get_user_model()

LIMIT_POSTS = getattr(settings, 'LIMIT_POSTS', 10)


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    current_time = timezone.now()
    if request.user.username != username:
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=current_time
        )

    paginator = Paginator(posts, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for post in page_obj.object_list:
        post.comment_count = post.comments.count()

    return render(
        request,
        'blog/profile.html', {
            'profile': user, 'page_obj': page_obj
        })


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


@login_required
def password_change_view(request, username):
    user = request.user
    form = PasswordChangeForm(user, request.POST)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('blog:password_change_done')
    return render(
        request,
        'blog/password_change_form.html', {'form': PasswordChangeForm(user)})


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

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
        })


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        object = super().get_object()
        if self.request.user != object.author and (
            not object.is_published or not
            object.category.is_published
        ):
            raise Http404()
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


def index(request):
    post = Post.objects.select_related('category').filter(
        pub_date__lte=timezone.now(),
        is_published=True, category__is_published=True
    )
    paginator = Paginator(post, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for post in page_obj.object_list:
        post.comment_count = post.comments.count()

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = category.posts.select_related('category').filter(
        is_published=True,
        pub_date__lte=timezone.now()
    )
    paginator = Paginator(post_list, LIMIT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    return render(
        request, 'blog/comment.html', {
            'form': CommentForm(instance=comment),
            'comment': comment, 'is_edit': True
        }
    )


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
