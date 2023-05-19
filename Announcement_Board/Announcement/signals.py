from django.db.models.signals import post_save
from django.dispatch import receiver  # импортируем нужный декоратор
from .tasks import send_mail_post
from .models import ResponseToAnnounce


# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
@receiver(post_save, sender=ResponseToAnnounce)
def notify_author_response(sender, instance, created, **kwargs):
    if created:
        email = [instance.response_announcement.author.email]
        send_mail_post.apply_async((instance.text, email))

    