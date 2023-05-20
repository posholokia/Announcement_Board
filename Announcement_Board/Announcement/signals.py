from django.db.models.signals import post_save
from django.dispatch import receiver  # импортируем нужный декоратор
from .tasks import send_mail_response, send_mail_accept_resp
from .models import ResponseToAnnounce


# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
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

    