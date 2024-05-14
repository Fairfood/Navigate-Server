from django.db import models
from django.contrib.gis.geos import GEOSGeometry

class GeoJSONField(models.JSONField):
    """
    A field for storing GeoJSON data.

    This field extends the Django JSONField to handle GeoJSON data.
    It provides methods to convert between GeoJSON strings and GEOSGeometry 
    objects.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        """
        Convert the GeoJSON string from the database to a GEOSGeometry object.

        Args:
            value (str): The GeoJSON string stored in the database.
            expression: The expression used to retrieve the value.
            connection: The database connection.

        Returns:
            GEOSGeometry: The converted GEOSGeometry object.
        """
        if value is None:
            return value
        # Convert GeoJSON string to GEOSGeometry object
        return GEOSGeometry(value)

    def to_python(self, value):
        """
        Convert the value to a GEOSGeometry object.

        Args:
            value: The value to be converted.

        Returns:
            GEOSGeometry: The converted GEOSGeometry object.
        """
        if isinstance(value, dict):
            # If value is a dictionary (GeoJSON), create GEOSGeometry object
            return GEOSGeometry(value)
        elif isinstance(value, GEOSGeometry):
            # If value is already a GEOSGeometry object, return as it is
            return value
        return None

    def get_prep_value(self, value):
        """
        Convert the GEOSGeometry object to a GeoJSON string.

        Args:
            value: The GEOSGeometry object to be converted.

        Returns:
            str: The converted GeoJSON string.
        """
        if value is None:
            return value
        # Convert GEOSGeometry object to GeoJSON string
        return value.geojson
    
class LatLongField(models.CharField):
    """
    A field for storing latitude and longitude coordinates.

    This field extends the `models.CharField` and provides methods for 
    converting between string representation and tuple representation of 
    latitude and longitude.

    Attributes:
        description (str): A description of the field.

    """

    description = "A field for storing latitude and longitude coordinates"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 40)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        """
        Converts the stored value from the database to a Python object.

        Args:
            value: The value retrieved from the database.
            expression: The expression used to retrieve the value.
            connection: The database connection.

        Returns:
            A tuple containing the latitude and longitude values as floats.
            If the value is None, it is returned as is.

        """
        if value is None:
            return value
        # Splitting the stored value into latitude and longitude
        return tuple(map(float, value.split(',')))

    def to_python(self, value):
        """
        Converts the given value to a Python representation.

        Args:
            value: The value to be converted.

        Returns:
            If the value is a string, it splits the string into latitude and 
            longitude and returns them as a tuple of floats.
            If the value is already a tuple or list, it returns it as it is.
            If the value is not a string, tuple, or list, it returns None.
        """
        if isinstance(value, str):
            # Splitting the stored value into latitude and longitude
            return tuple(map(float, value.split(',')))
        elif isinstance(value, (tuple, list)):
            # Already a tuple or list, return as it is
            return value
        return None

    def get_prep_value(self, value):
        """
        Returns the prepared value for the field before storing it in the 
        database.
        
        Args:
            value: The value to be prepared.
            
        Returns:
            The prepared value.
        """
        if value is None:
            return value
        # Converting tuple of latitude and longitude to string before storing
        return ','.join(str(coord) for coord in value)

    def value_to_string(self, obj):
        """
        Converts the value of the field to a string representation.

        Args:
            obj: The object from which to retrieve the value.

        Returns:
            A string representation of the field's value.
        """
        value = self.value_from_object(obj)
        return self.get_prep_value(value)