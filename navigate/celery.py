"""Celery configurations are specified here."""

from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navigate.settings")

app = Celery(
    "navigate",
    broker=f"{settings.REDIS_URL}:{settings.REDIS_PORT}",
    backend=f"{settings.REDIS_URL}:{settings.REDIS_PORT}",
)
BROKER_URL = f"{settings.REDIS_URL}:{settings.REDIS_PORT}/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Configure Celery using settings from Django settings.py.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.timezone = "UTC"
# Load tasks from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.broker_connection_retry_on_startup = True
