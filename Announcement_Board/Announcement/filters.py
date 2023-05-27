from django_filters import FilterSet, CharFilter, DateFilter
from .models import ResponseToAnnounce
from django.forms.widgets import DateInput


class ResponseFilter(FilterSet):
    announce_title = CharFilter(field_name='response_announcement__title',
                                label='Заголовок объявления',
                                lookup_expr='iexact')
    announce_date = DateFilter(field_name='date_time_resp',
                               label='Дата отклика',
                               lookup_expr='date',
                               widget=DateInput(
                                   format='%Y-%m-%d',
                                   attrs={'type': 'date'}, )
                               )

    class Meta:
        model = ResponseToAnnounce
        fields = ['announce_title', 'announce_date']
