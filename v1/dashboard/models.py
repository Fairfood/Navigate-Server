from django.db import models
from base.models import AbstractBaseModel

from v1.supply_chains.models.nodes import Company
from . import constants

class Theme(AbstractBaseModel):
    """
    Represents a theme for a company in the dashboard.

    Attributes:
        company (ForeignKey): The company associated with the theme.
        name (CharField): The name of the theme.
        title (CharField): The title of the theme.
        primary_color (CharField): The primary color of the theme.
        primary_light_color (CharField): The light version of the primary 
            color.
        secondary_color (CharField): The secondary color of the theme.
        stroke_color (CharField): The stroke color of the theme.
        first_font_color (CharField): The first font color of the theme.
        second_font_color (CharField): The second font color of the theme.
        third_font_color (CharField): The third font color of the theme.
        info_color (CharField): The info color of the theme.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE, 
                                related_name="themes")
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, default=constants.THEME_TITLE)
    primary_color = models.CharField(max_length=7)
    primary_light_color = models.CharField(max_length=7)
    secondary_color = models.CharField(max_length=7)
    stroke_color = models.CharField(max_length=7)
    first_font_color = models.CharField(max_length=7)
    second_font_color = models.CharField(max_length=7)
    third_font_color = models.CharField(max_length=7)
    info_color = models.CharField(max_length=7)

    def __str__(self) -> str:
        return f'{self.name}:{self.company}'

class Intervention(AbstractBaseModel):
    """
    Represents an intervention in the system.

    Attributes:
        company (ForeignKey): The company associated with the intervention.
        name (CharField): The name of the intervention.
        description (CharField): The description of the intervention.
        short_description (CharField): The short description of the 
            intervention.
        more_url (URLField): The URL for more information about the 
            intervention.
        image (ImageField): The image associated with the intervention.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE, 
                                related_name="interventions")
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    short_description = models.CharField(max_length=255)
    more_url = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to="intervention_images", 
                              null=True, blank=True)
    
    def __str__(self) -> str:
        return self.name

