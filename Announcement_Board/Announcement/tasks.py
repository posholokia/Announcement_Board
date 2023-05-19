from django.template.loader import render_to_string
from celery import shared_task
from Announcement_Board import settings
from django.core.mail import EmailMultiAlternatives
# import datetime
# from news.models import Post, Category


@shared_task
def send_mail_response(text, email, author, announce):
    html_content = render_to_string(
        'send_mail_response.html',
        {
            'text': text[:49],
            'author': author,
            'announce': announce,
            'link': f'{settings.SITE_URL}/board/my_announcement/responses'
        }
    )
    msg = EmailMultiAlternatives(
        subject='Новый отклик на Ваше объявление!',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=email,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    
    