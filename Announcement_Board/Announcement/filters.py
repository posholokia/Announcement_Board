from django_filters import FilterSet, CharFilter, DateFilter, ChoiceFilter, BooleanFilter
from .models import ResponseToAnnounce
from django.forms.widgets import DateInput


class RespToMyAnnounceFilter(FilterSet):
    announce_title = CharFilter(field_name='response_announcement__title',
                                label='Поиск по объявлению',
                                lookup_expr='iexact',
                                )
    announce_date = DateFilter(field_name='date_time_resp',
                               label='Дата отклика',
                               lookup_expr='date',
                               widget=DateInput(
                                   format='%Y-%m-%d',
                                   attrs={'type': 'date'}, )
                               )
    STATUS_CHOICES = (
        (1, 'Принято'),
        (2, 'Отклонено'),
        (0, 'Не рассмотрено')
    )
    accepted = ChoiceFilter(field_name='accepted',
                            lookup_expr='exact',
                            label='Статус',
                            choices=STATUS_CHOICES,
                            empty_label='Выберите статус'
                            )

    class Meta:
            model = ResponseToAnnounce
            fields = ['announce_title', 'announce_date', 'accepted']


class MyResponseFilter(FilterSet):
    announce_title = CharFilter(field_name='response_announcement__title',
                                label='Заголовок объявления',
                                lookup_expr='iexact',
                                )
    announce_date = DateFilter(field_name='date_time_resp',
                               label='Дата отклика',
                               lookup_expr='date',
                               widget=DateInput(
                                   format='%Y-%m-%d',
                                   attrs={'type': 'date'}, )
                               )
    STATUS_CHOICES = (
        (1, 'Принято'),
        (2, 'Отклонено'),
        (0, 'Не рассмотрено')
    )
    accepted = ChoiceFilter(field_name='accepted',
                            lookup_expr='exact',
                            label='Статус',
                            choices=STATUS_CHOICES,
                            empty_label='Выберите статус'
                            )

    class Meta:
        model = ResponseToAnnounce
        fields = ['announce_title', 'announce_date', 'accepted']
