import math

from pyproj import Transformer
from shapely.geometry import Polygon, mapping
from shapely.ops import transform


class HexagonUtils:
    def calculate_hex_radius(self, area_in_ha):
        """
        Calculate the radius of a hexagon based on its area.

        Args:
            area_in_ha (float): Area of the hexagon in hectares (1 hectare = 10,000 square meters).

        Returns:
            float: The radius of the hexagon in meters.
        """
        # Convert the area from hectares to square meters
        area_in_sqm = area_in_ha * 10000

        # The formula for the area of a regular hexagon is:
        # (3 * sqrt(3) / 2) * r^2
        # Rearrange to solve for r:
        # r = sqrt((2 * area) / (3 * sqrt(3)))
        radius = math.sqrt((2 * area_in_sqm) / (3 * math.sqrt(3)))

        return radius

    def create_hexagon(self, lat, lon, area_in_ha):
        """
        Create a hexagon centered at a given latitude and longitude with a specified area.

        Args:
            lat (float): Latitude of the center point.
            lon (float): Longitude of the center point.
            area_in_ha (float): Desired area of the hexagon in hectares.

        Returns:
            shapely.geometry.Polygon: The hexagon as a polygon in lat/lon coordinates.
        """
        # Calculate the radius needed for a hexagon with the given area
        radius = self.calculate_hex_radius(area_in_ha)

        # Set up transformers to switch between lat/lon (WGS84) and UTM (projected) coordinates
        transformer_to_utm = Transformer.from_crs("epsg:4326", "epsg:32633", always_xy=True)
        transformer_to_latlon = Transformer.from_crs("epsg:32633", "epsg:4326", always_xy=True)

        # Convert the center lat/lon point to UTM coordinates for geometric calculations
        utm_center = transformer_to_utm.transform(lon, lat)

        # Create a hexagon in UTM coordinates centered at the UTM-transformed point
        hexagon = Polygon([
            (utm_center[0] + radius * math.cos(angle),  # X-coordinate
             utm_center[1] + radius * math.sin(angle))  # Y-coordinate
            for angle in [math.radians(60 * i) for i in range(6)]  # Divide 360° into 6 angles
        ])

        # Convert the hexagon from UTM back to lat/lon (WGS84)
        hexagon_latlon = transform(transformer_to_latlon.transform, hexagon)

        return hexagon_latlon

    def polygon_to_geojson(self, polygon):
        """
        Convert a polygon to a GeoJSON feature.

        Args:
            polygon (shapely.geometry.Polygon): The polygon to convert.

        Returns:
            dict: GeoJSON geometry representation of the polygon.
        """

        return mapping(polygon)

    def coord_to_poly(self, latitude, longitude, area_in_ha=0.25):
        """
        Create a hexagonal polygon around a coordinate and return it as a GeoJSON object.

        Args:
            latitude (float): Latitude of the center point.
            longitude (float): Longitude of the center point.
            area_in_ha (float, optional): Desired area of the hexagon in hectares. Defaults to 0.25 ha.

        Returns:
            dict: GeoJSON geometry representation of the hexagon.
        """
        # Create the hexagonal polygon
        hex_polygon = self.create_hexagon(latitude, longitude, area_in_ha)

        # Convert the polygon to a GeoJSON feature
        geojson_output = self.polygon_to_geojson(hex_polygon)

        return geojson_output
