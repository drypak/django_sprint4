from blog.managers import PublishedManager
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from blogicum.constants import MAX_LENGTH_NAME, MAX_STR_LENGTH, MAX_TEXT_LENGTH

User = get_user_model()


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        ordering = ['-created_at']
        abstract = True


class Location(BaseModel):
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название места'
    )

    class Meta(BaseModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:MAX_STR_LENGTH]


class Category(BaseModel):
    title = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Заголовок',
        help_text='Название категории, которое будет отображаться на сайте.'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        help_text='Описание категории (необязательно).'
    )

    class Meta(BaseModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:MAX_STR_LENGTH]

    def short_description(self):
        return self.description[:MAX_TEXT_LENGTH]

    short_description.admin_order_field = 'description'


class Post(BaseModel):
    title = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время'
                  ' в будущем — можно делать отложенные публикации.',
        default=timezone.now
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        null=True,
        related_name='posts',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение'
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
    )

    objects = models.Manager()
    published = PublishedManager()

    class Meta(BaseModel.Meta):
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self):
        return f'{self.title[:MAX_STR_LENGTH]}'

    def get_absolute_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.author.username})


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Выберите пост, к которому относится комментарий',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Profile(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
