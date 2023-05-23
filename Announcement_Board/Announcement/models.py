from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from ckeditor.fields import RichTextField
from django.urls import reverse
from django.contrib.auth.models import User


class Announcement(models.Model):
    CATEGORY = (
        ('Tank', 'Танки'),
        ('Healer', 'Хилы'),
        ('DD', 'ДД'),
        ('Vendor', 'Торговцы'),
        ('GuildMaster', 'Гильдмастеры'),
        ('QuestGiver', 'Квестгиверы'),
        ('Smith', 'Кузнецы'),
        ('Skinner', 'Кожевники'),
        ('Alchemist', 'Зельевары'),
        ('SpellMaster', 'Мастера заклинаний'),
    )
    author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE)
    category = models.CharField(max_length=16, choices=CATEGORY)
    title = models.CharField(max_length=64)
    text = RichTextUploadingField(null=True, config_name='default')
    published_date = models.DateField(auto_now_add=True)
    sent_mail = models.BooleanField(default=False)
    
    def get_absolute_url(self):
        return reverse('announce', args=[str(self.id)])

    def __str__(self):
        return f'{self.title}'

    def preview(self):
        return f'{self.text[0:49]}'
    

class ResponseToAnnounce(models.Model):
    response_announcement = models.ForeignKey('Announcement', related_name='response', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    text = models.TextField(max_length=256)
    accepted = models.BooleanField(null=True, default=None)
    
    def accept(self):
        self.accepted = True
        self.save()
        
    def decline(self):
        self.accepted = False
        self.save()
    
    def get_absolute_url(self):
        return reverse('announce', args=[str(self.response_announcement.id)])

    def __str__(self):
        return f'{self.text[0:9]}'
    