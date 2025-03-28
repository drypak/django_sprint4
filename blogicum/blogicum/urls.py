from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView
from blog.forms import CustomUserCreationForm

auth_urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=CustomUserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    *auth_urlpatterns,
]
# Обработчики ошибок
handler403 = 'pages.views.error_403'
handler404 = 'pages.views.error_404'
handler500 = 'pages.views.error_500'
