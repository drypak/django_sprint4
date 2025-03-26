from django.core.paginator import Paginator


def get_paginated_page(request, queryset, limit=10):

    paginator = Paginator(queryset, limit)
    page_number = request.GET.get('page')
    page_pbj = paginator.get_page(page_number)
    return page_pbj
