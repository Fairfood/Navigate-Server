from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class SyncStatus(models.IntegerChoices):
    STARTED = 1
    FAILED = 2
    IN_QUEUE = 3
    COMPLETED = 4