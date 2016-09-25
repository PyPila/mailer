from django import template

register = template.Library()


@register.filter
def none(value):
    if value is None:
        return ''
    return value
