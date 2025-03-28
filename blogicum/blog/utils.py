from django.core.paginator import Paginator

from blogicum.settings import LIMIT_POSTS


def get_paginated_page(request, queryset, limit=LIMIT_POSTS):
    return Paginator(queryset, limit).get_page(request.GET.get('page'))
