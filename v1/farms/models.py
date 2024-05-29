from django.db import models
from base.models import AbstractAddressModel
from base.models import AbstractBaseModel
from v1.supply_chains.models.nodes import Farmer
from .managers import FarmQuerySet
from .managers import FarmCommentQuerySet
from .constants import Pillers

class Farm(AbstractAddressModel):
    """
    Represents a farm.

    Attributes:
        farm_type (str): The type of the farm.
        farmer (Farmer): The farmer associated with the farm.
        external_id (str): The external ID of the farm.
        latlong (LatLongField): The latitude and longitude of the farm.
        geo_json (GeoJSONField): The geoJSON data of the farm.
        analysis_radius (float): The analysis radius of the farm.
    """

    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, 
                               related_name="farms")
    external_id = models.CharField(max_length=255)
    geo_json = models.JSONField(blank=True, null=True)
    analysis_radius = models.FloatField(null=True, blank=True)

    objects = FarmQuerySet.as_manager()

    def __str__(self) -> str:
        """
        Returns a string representation of the farm.

        Returns:
            str: The string representation of the farm.
        """
        return f"{self.farmer} - {self.external_id}"
    
class FarmProperty(AbstractBaseModel):
    """
    Represents the properties of a farm.

    Attributes:
        farm (Farm): The farm associated with the properties.
        total_area (float): The total area of the farm.
        primary_forest_area (float): The area of primary forest in the farm.
        tree_cover_extent (float): The extent of tree cover in the farm.
        protected_area (float): The area of protected land in the farm.
    """

    farm = models.OneToOneField(Farm, on_delete=models.CASCADE, 
                             related_name="property")
    total_area = models.FloatField(default=0.0, null=True, blank=True)
    primary_forest_area = models.FloatField(default=0.0, null=True, blank=True)
    tree_cover_extent = models.FloatField(default=0.0, null=True, blank=True)
    protected_area = models.FloatField(default=0.0, null=True, blank=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the farm properties.

        Returns:
            str: The string representation of the farm properties.
        """
        return f"{self.farm} - {self.total_area}"    
    
class FarmComment(AbstractBaseModel):
    """
    Represents a comment on a farm.

    Attributes:
        farm (Farm): The farm associated with the comment.
        comment (str): The comment text.
        file (FileField): The file attached to the comment.
        source (str): The source of the comment.
    """

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, 
                             related_name="comments")
    comment = models.TextField()
    file = models.FileField(upload_to="farm_comments", null=True, blank=True)
    source = models.CharField(max_length=255)
    piller = models.CharField(max_length=255, 
                              choices=Pillers.choices)
    
    objects = FarmCommentQuerySet.as_manager()

    def __str__(self) -> str:
        """
        Returns a string representation of the farm comment.

        Returns:
            str: The string representation of the farm comment.
        """
        return f"{self.farm} - {self.source}"



class DeforestationSummary(AbstractBaseModel):
    """
    Represents a summary of deforestation on a farm.

    Attributes:
        farm (Farm): The farm associated with the deforestation summary.
        name (str): The name of the deforestation summary.
        year (int): The year of the deforestation summary.
        canopy_density (float): The canopy density of the deforestation.
        source (str): The source of the deforestation summary.
        value (float): The value of the deforestation summary.
    """

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE,
                             related_name="deforestation_summaries")
    name = models.CharField(max_length=255)
    year = models.IntegerField(default=2014)
    canopy_density = models.FloatField(default=0.0)
    source = models.CharField(max_length=255)
    value = models.FloatField(default=0.0)

    def __str__(self) -> str:
        """
        Returns a string representation of the deforestation summary.

        Returns:
            str: The string representation of the deforestation summary.
        """
        return f"{self.farm} - {self.name} - {self.year}"

