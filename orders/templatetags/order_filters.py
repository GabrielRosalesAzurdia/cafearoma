from django import template

register = template.Library()

@register.filter
def filter_by_status(queryset, status):
    """Filtra un queryset de órdenes por estado"""
    return queryset.filter(status=status)