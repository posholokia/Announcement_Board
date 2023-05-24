from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_mail_response, send_mail_accept_resp, send_mailing
from .models import ResponseToAnnounce, Announcement
from django.contrib.auth.models import User


@receiver(post_save, sender=ResponseToAnnounce)
def notify_author_response(sender, instance, created, **kwargs):
    if created:
        author = instance.response_announcement.author.username
        announce = instance.response_announcement.title
        email = [instance.response_announcement.author.email]
        send_mail_response.apply_async((instance.text, email, author, announce))
        
        
@receiver(post_save, sender=ResponseToAnnounce)
def notify_accept_response(sender, instance, created, **kwargs):
    if not created and instance.accepted:
        announce = instance.response_announcement.title
        email = [instance.response_announcement.author.email]
        pk = instance.response_announcement.id
        username = instance.user.username
        send_mail_accept_resp.apply_async((email, announce, pk, username))


@receiver(post_save, sender=Announcement)
def notify_accept_response(sender, instance, created, **kwargs):
    if created and instance.sent_mail:  # проверяем, что при создании проставлена отметка об отправке рассылки
        title = instance.title
        text = instance.text
        # получим список всех почтовых ящиков пользователей
        email_qs = User.objects.values_list('email').exclude(email='')  # исключим пустые поля почты у суперюзеров
        email = [email[0] for email in email_qs]  # распаковываем qs в список. qs состоит из одиночных кортежей
        pk = instance.id
        send_mailing.apply_async((email, title, pk, text))
