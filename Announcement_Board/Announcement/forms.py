from django import forms
from .models import Announcement, ResponseToAnnounce
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.models import User


class AnnouncementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """
        При инициализации формы проверяем к какой группе относится пользователь.
        Для суперюзера в форме появляется булево поле для отправки письма всем пользователям
        Полученный kwargs должен быть удален, т.к. в __init__ родительского класса он отсутсвует,
        иначе будет ошибка инициализации формы
        """
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        if user not in User.objects.filter(username='admin'):  # TODO изменить на группу пользователей
            self.fields['sent_mail'].widget = forms.HiddenInput()

    class Meta:
        model = Announcement
        fields = ['category', 'title', 'text', 'sent_mail']
        print(fields)
        exclude = []
        labels = {
            'category': 'Категория',
            'title': 'Заголовок',
            'text': 'Текст',
            'sent_mail': 'Отправить письмо пользователям',
        }


        

class ResponseForm(forms.ModelForm):
    class Meta:
        model = ResponseToAnnounce
        fields = ['text', ]
        