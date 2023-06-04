from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
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
    published_date = models.DateTimeField(auto_now_add=True, name='date')
    sent_mail = models.BooleanField(default=False)
    opportunity_to_response = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('announce', args=[str(self.id)])

    def __str__(self):
        return f'{self.title}'

    def preview(self):
        return f'{self.text[0:19]}'


class ResponseToAnnounce(models.Model):
    """
    Модель отклика на объявление
    accepted: статус отклика. 0 - не рассмотрено (по умолчанию), 1 - принято, 2 - отклонено.
    Реализовано через Integer вместо Boolean для реализации филтров, где требуется 4 состояния: отсутствие фильтра,
    "не рассмотрено", "отклонено" и "принято". В Boolean иожно передать только 3 состояния: None, True, False,
    из-за чего отсутсвие фильтра и "не рассмотрено" возвращают одинаковый набор объектов
    """
    response_announcement = models.ForeignKey('Announcement', related_name='response', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    text = models.TextField(max_length=256)
    accepted = models.IntegerField(default=0)
    date_time_resp = models.DateField(auto_now_add=True, null=True)

    def accept(self):
        self.accepted = 1
        self.save()

    def decline(self):
        self.accepted = 2
        self.save()

    def get_absolute_url(self):
        return reverse('announce', args=[str(self.response_announcement.id)])

    def __str__(self):
        return f'{self.text[0:19]}'
