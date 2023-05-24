from django import forms
from .models import Announcement, ResponseToAnnounce
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.models import User


class AnnouncementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """
        При инициализации формы проверяем к какой группе относится пользователь.
        Для суперюзера в форме появляется поле для отправки письма всем пользователям.
        Полученный kwargs должен быть удален, т.к. в __init__ родительского класса он отсутсвует,
        иначе будет ошибка инициализации формы.
        Необходимо значение по умолчанию когда ключ отсутсвует, т.к. __init__ вызывается дважды: при переходе
        на страницу и после отправке формы.
        sent_mail=False в модели по умолчанию
        opportunity_to_response=False в модели по умолчанию
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user not in User.objects.filter(username='admin'):  # TODO изменить на группу пользователей
            self.fields['sent_mail'].widget = forms.HiddenInput()
            self.fields['opportunity_to_response'].widget = forms.HiddenInput()

    class Meta:
        model = Announcement
        fields = ['category', 'title', 'text', 'sent_mail', 'opportunity_to_response']
        exclude = []
        labels = {
            'category': 'Категория',
            'title': 'Заголовок',
            'text': 'Текст',
            'sent_mail': 'Отправить письмо пользователям',
            'opportunity_to_response': "Пользователю могут отправлять отклик?"
        }


class ResponseForm(forms.ModelForm):
    class Meta:
        model = ResponseToAnnounce
        fields = ['text', ]
        