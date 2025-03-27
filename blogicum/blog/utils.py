from django.core.paginator import Paginator

from blogicum.settings import LIMIT_POSTS


def get_paginated_page(request, queryset, limit=LIMIT_POSTS):
    paginator = Paginator(queryset, limit)
    page_number = request.GET.get('page')
    page_pbj = paginator.get_page(page_number)
    return page_pbj
