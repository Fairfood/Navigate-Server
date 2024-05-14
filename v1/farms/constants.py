from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


Pillers = models.TextChoices('Pillers', 'DEFORESTATION ')

FarmType = models.TextChoices('FarmType', 'POINT POLYGON')


template_files = {
    Pillers.DEFORESTATION: "v1.templates.deforestation"
}