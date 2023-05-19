import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Announcement_Board.settings')

app = Celery('Announcement_Board')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
