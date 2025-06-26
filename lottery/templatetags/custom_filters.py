from django import template

register = template.Library()

@register.filter(name='split')
def split(value, delimiter=' '):
    return value.split(delimiter)