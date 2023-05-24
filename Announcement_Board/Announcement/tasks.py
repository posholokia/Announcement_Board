from django.template.loader import render_to_string
from celery import shared_task
from Announcement_Board import settings
from django.core.mail import EmailMultiAlternatives
# import datetime



@shared_task
def send_mail_response(text, email, author, announce):
    html_content = render_to_string(
        'send_mail_response.html',
        {
            'text': text[:49],
            'author': author,
            'announce': announce,
            'link': f'{settings.SITE_URL}/board/my_announcement/responses/'
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
    

@shared_task
def send_mail_accept_resp(email, announce, pk, username):
    html_content = render_to_string(
        'send_mail_accept_resp.html',
        {
            'announce': announce,
            'username': username,
            'link': f'{settings.SITE_URL}/board/{pk}/'
        }
    )
    msg = EmailMultiAlternatives(
        subject='Ваш отклик принят!',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=email,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def send_mailing(email, title, pk, text):
    html_content = render_to_string(
        'send_mailing.html',
        {
            'title': title,
            'text': text,
            'link': f'{settings.SITE_URL}/board/{pk}/'
        }
    )
    msg = EmailMultiAlternatives(
        subject='Новое объявление от MMORPG',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=email,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()