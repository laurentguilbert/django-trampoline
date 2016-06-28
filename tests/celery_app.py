"""
Celery app for trampoline tests.
"""
from celery import Celery

from django.conf import settings

app = Celery('trampoline')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
