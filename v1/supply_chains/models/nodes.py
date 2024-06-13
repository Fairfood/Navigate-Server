from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from base.models import AbstractAddressModel, AbstractBaseModel
from v1.farms.constants import Pillers

def default_piller():
    """
    Returns the default piller for the supply chain nodes.

    Returns:
        list: A list containing the default piller.
    """
    return [Pillers.DEFORESTATION]

class SupplyChain(AbstractBaseModel):
    """
    Represents a supply chain in the system.

    Attributes:
        name (CharField): A field to store the name of the supply chain.
        image (ImageField): An image field to store the supply chain's image.
    """

    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="supply_chain_images", null=True, blank=True)

    def __str__(self) -> str:
        return self.name

class Company(AbstractAddressModel):
    """
    Represents a company in the supply chain system.

    Attributes:
        image (ImageField): An image field to store the company's image.
        name (CharField): A field to store the name of the company.
        users (ManyToManyField): A many-to-many relationship to the User model.
        supply_chains (ManyToManyField): A many-to-many relationship to the 
            SupplyChain model.
        pillers (JSONField): A field to store the company's pillers.
    """

    image = models.URLField(null=True, blank=True)
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="companies"
    )
    supply_chains = models.ManyToManyField(
        SupplyChain, related_name="companies"
    )
    pillers = models.JSONField(default=default_piller, 
                               null=True, blank=True)
    sso_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.name
    
class Farmer(AbstractAddressModel):
    """
    Represents a farmer in the supply chain system.

    Attributes:
        image (ImageField): An image field to store the farmer's image.
        external_id (CharField): A field to store an external identifier for 
            the farmer.
        name (CharField): A field to store the name of the farmer.
        company (ForeignKey): A foreign key relationship to the Company model.
        supply_chains (ManyToManyField): A many-to-many relationship to the 
            SupplyChain model.

    Methods:
        add_supply_chain(supply_chain): Adds a supply chain to the farmer's 
            list of supply chains.

    """

    image = models.FileField(upload_to="farmer_images", null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    company = models.ForeignKey(
        Company, related_name="farmers", on_delete=models.CASCADE
    )
    supply_chains = models.ManyToManyField(
        SupplyChain, related_name="farmers", blank=True
    )

    def __str__(self) -> str:
        return self.name
    
    def add_supply_chain(self, supply_chain):
        """
        Adds a supply chain to the farmer's list of supply chains.

        Args:
            supply_chain (SupplyChain): The supply chain to be added.

        Raises:
            ValidationError: If the company does not have access to the 
                supply chain.

        """

        if supply_chain not in self.company.supply_chains.all():
            self.company.supply_chains.add(supply_chain)
        self.supply_chains.add(supply_chain)