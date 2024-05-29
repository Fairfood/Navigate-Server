from django.db import models
from base.models import AbstractBaseModel
from ..models.nodes import Farmer
from ..managers import BatchQuerySet

class Batch(AbstractBaseModel):
    """
    Represents a batch in the supply chain.

    Attributes:
        external_id (str): The external ID of the batch.
        farmers (ManyToManyField): The farmers associated with the batch.
        supply_chain (ForeignKey): The supply chain to which the batch belongs.
    """

    external_id = models.CharField(max_length=255)
    farmers = models.ManyToManyField(Farmer, related_name="batches", 
                                     blank=True)
    supply_chain = models.ForeignKey(
        "supply_chains.SupplyChain", on_delete=models.CASCADE, 
        related_name="batches"
    )

    objects = BatchQuerySet.as_manager()

    def __str__(self) -> str:
        return self.external_id

