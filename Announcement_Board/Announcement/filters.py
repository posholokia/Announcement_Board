from django_filters import FilterSet, CharFilter
from .models import ResponseToAnnounce


class ResponseFilter(FilterSet):
    announce_title = CharFilter(field_name='response_announcement__title', label='Заголовок объявления', lookup_expr='iexact')  # TODO доделать фильтры
    
    class Meta:
        model = ResponseToAnnounce
        fields = [
            'announce_title'
        ]
