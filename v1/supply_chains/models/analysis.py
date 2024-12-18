from django.db import models

from base.models import AbstractBaseModel
from v1.farms.models import Farm

from .. import constants


class AnalysisQueue(AbstractBaseModel):
    """
    Represents a batch in the supply chain.

    Attributes:
        external_id (str): The external ID of the batch.
        farmers (ManyToManyField): The farmers associated with the batch.
        supply_chain (ForeignKey): The supply chain to which the batch belongs.
    """

    farm = models.ManyToManyField(Farm, related_name="analysis_queue")
    status = models.IntegerField(choices=constants.SyncStatus, default=constants.SyncStatus.IN_QUEUE)

    def __str__(self) -> str:
        return f"{str(self.id)} - {str(self.status)}"

