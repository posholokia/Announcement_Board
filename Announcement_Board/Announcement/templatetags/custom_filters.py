from django import template

register = template.Library()


@register.filter()
def slice_qs(qs, obj):
    return qs.filter(response_announcement=obj)
