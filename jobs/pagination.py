"""
自定义分页类
"""

from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    自定义分页类，允许客户端通过 page_size 参数自定义每页大小
    """
    page_size = 20  # 默认每页20条
    page_size_query_param = 'page_size'  # 允许客户端通过此参数自定义每页大小
    max_page_size = 100  # 最大每页100条
