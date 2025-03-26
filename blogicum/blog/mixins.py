from blog.forms import PostForm
from blog.models import Post
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class AuthorRequiredMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs['post_id'])
