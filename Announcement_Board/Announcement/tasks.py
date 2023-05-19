from django.template.loader import render_to_string
from celery import shared_task
from Announcement_Board import settings
from django.core.mail import EmailMultiAlternatives
# import datetime
# from news.models import Post, Category


@shared_task
def send_mail_post(text, email):
    html_content = render_to_string(
        'send_mail_response.html',
        {
            'text': text[:49],
        }
    )
    msg = EmailMultiAlternatives(
        subject='67886',
        body='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=email,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    
    