from django import forms
from .models import Announcement, ResponseToAnnounce
from ckeditor.widgets import CKEditorWidget


class AnnouncementForm(forms.ModelForm):
    # content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Announcement
        # fields = '__all__'
        exclude = ('author', )
        

class ResponseForm(forms.ModelForm):
    class Meta:
        model = ResponseToAnnounce
        fields = ['text', ]
        