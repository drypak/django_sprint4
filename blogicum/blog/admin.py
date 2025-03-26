from django.contrib import admin

from .models import Category, Comment, Location, Post, Profile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    search_fields = ('title', 'slug')
    list_filter = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'is_published')
    search_fields = ('name',)
    list_filter = ('is_published',)
    ordering = ('-created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'pub_date',
        'is_published', 'created_at',
        'category', 'location')

    search_fields = ('title', 'author__username', 'category__title')
    list_filter = ('pub_date', 'category', 'location')
    ordering = ('-pub_date',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('post__title', 'author__username', 'text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
