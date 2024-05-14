from django.db import models
from base.models import AbstractBaseModel

from v1.supply_chains.models.nodes import Company

class Theme(AbstractBaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, 
                                related_name="themes")
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=8)

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

