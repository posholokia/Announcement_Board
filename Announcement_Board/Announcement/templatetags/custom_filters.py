from django import template

register = template.Library()


# фильтр возвращает количество откликов к выбранному объявлению
@register.filter()
def slice_qs(qs, obj):
    return len(qs.filter(response_announcement=obj))
