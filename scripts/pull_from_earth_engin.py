import ee
import math
from shapely.geometry import Polygon, mapping
from shapely.ops import transform
from pyproj import Transformer
from django.apps import apps
from django.conf import settings
from v1.farms.models import YearlyTreeCoverLoss

credentials = ee.ServiceAccountCredentials(
    settings.EE_SERVICE_ACCOUNT, settings.EE_SERVICE_ACCOUNT_CREDENTIAL_PATH)
ee.Initialize(credentials)

class ForestAnalyzer():
    """
    Wrapper class to do the forest analysis using Earth Engine.
    Attributes:
        polygon (ee.Geometry): The polygon to analyze.
        buffer_area (int): The buffer area around the polygon.
        canopy_dens (int): The canopy density threshold.
        dataset_tree_cover (ee.Image): The tree cover data set.
        dataset_primary_forest (ee.ImageCollection):
            The primary forest data set.
        dataset_protected_areas (ee.FeatureCollection):
            The protected areas data set.

    """
    polygon = None
    buffer_area = 0
    canpoy_dens = 30
    _buffer_poly = None
    dataset_tree_cover = ee.Image(
        "UMD/hansen/global_forest_change_2023_v1_11")
    dataset_primary_forest = ee.ImageCollection(
        "UMD/GLAD/PRIMARY_HUMID_TROPICAL_FORESTS/v1").mosaic().selfMask()
    dataset_protected_areas = ee.FeatureCollection(
        "WCMC/WDPA/current/polygons")

    def __init__(self, geo_json, buffer_area=0, canopy_dens=30):
        """
        Constructor for the ForestAnalyzer class.

        When the class is instantiated, the constructor sets the polygon,
        load the data sets and also buffer the area around the polygon if
        buffer area is specified.

        Args:
            geo_json (dict): The geojson data of the polygon.
            buffer_area (int): The buffer area around the polygon.
            canopy_dens (int): The canopy density threshold.

        """

        if geo_json["type"] == "Point":
            geo_json = coord_to_poly(
                geo_json['coordinates'][0], geo_json['coordinates'][1])
            
        self.polygon = ee.Geometry.Polygon(geo_json["coordinates"][0])
        self.buffer_area = buffer_area
        self.canopy_dens = canopy_dens
        self._buffer_poly = self.polygon
        if buffer_area:
            self._buffer_poly = self.polygon.buffer(buffer_area)

    def calculate_tree_cover(self) -> float:
        """
        Function to calculate tree cover.

        This function processes a data set to measure the area of tree cover.
        It begins by selecting the 'treecover2000' band from the data and
        applies a specified threshold to identify tree cover. A binary mask,
        which highlights areas of tree cover, is then created and multiplied
        by the pixel area to compute the tree cover area in each pixel.
        The function reduces the region to sum the total tree cover area. Here
        Set an appropriate scale, matching the dataset resolution.
        Finally, the area sum is converted from square meters to hectares
        for easier interpretation.

        Returns:
            tree_cover_area_ha(float): The total tree cover area in hectares
                within the specified polygon.
        """
        tree_cover_extent = self.dataset_tree_cover.select(
            'treecover2000').gte(self.canopy_dens).clip(self._buffer_poly)

        pixel_area = ee.Image.pixelArea()
        tree_cover_pixel_area = tree_cover_extent.multiply(pixel_area)

        tree_cover_total_area = tree_cover_pixel_area.reduceRegion(
            reducer=ee.Reducer.sum(), geometry=self._buffer_poly,
            scale=30, maxPixels=1e9).getInfo()
        tree_cover_area_ha = tree_cover_total_area['treecover2000'] / 10000

        return tree_cover_area_ha

    def calculate_primary_forest(self) -> float:
        """
        Function to calculate primary forest area.

        This function calculates the area of primary forest within the specified
        polygon. It begins by clipping the primary forest data to the buffered.
        Calculate primary forest area. Convert from square meters to hectares.

        Returns
            primary_forest_area_ha(float): total primary forest area.
        """
        primary_forest_extent = self.dataset_primary_forest.clip(
            self._buffer_poly).unmask()

        primary_forest_pixel_area = primary_forest_extent.multiply(
            ee.Image.pixelArea())
        primary_forest_area = primary_forest_pixel_area.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=self._buffer_poly,
            scale=30,
            maxPixels=1e9
        ).getInfo()['Primary_HT_forests']

        primary_forest_area_ha = primary_forest_area / 10000

        return primary_forest_area_ha

    def calculate_protected_area(self):
        """
        Calculates the total protected area within a specified polygon.

        This function loads the 'WCMC/WDPA/current/polygons' dataset,
        which contains protected area information. It then filters these
        areas to find those that intersect with the specified polygon,
        defined by the 'polygon_coords' parameter. The function calculates
        the total area of these intersecting protected areas in square
        kilometers.

        Returns:
            total_area(float): The total area of protected regions within
                the specified polygon in square kilometers.

        """
        intersecting_areas = self.dataset_protected_areas.filterBounds(
            self._buffer_poly)

        area_calculator = intersecting_areas.map(
            lambda feature: feature.set(
                'area', feature.geometry().area().divide(1e6)))

        total_area = area_calculator.aggregate_sum('area')
        return total_area.getInfo()

    def calculate_yearly_tree_cover_loss(self):
        """
        Calculates the total tree cover loss for each year within the 
        specified polygon.This function processes the 'lossyear' band 
        from the dataset to determine the year of tree cover loss, 
        creates a binary mask to indicate areas of loss, and sums up the 
        area of loss for each year.The areas of loss are converted 
        from square meters to hectares .

        Returns:
            list of dict: Each dictionary contains the year and the 
            corresponding tree cover loss area in hectares.
        """

        # Select the 'lossyear' band which indicates the year of tree cover loss.
        loss_image = self.dataset_tree_cover.select(["loss"])
        tree_cover = self.dataset_tree_cover.select(["treecover2000"])
        loss_year = self.dataset_tree_cover.select(["lossyear"])

        # Mask the loss image to only consider areas with tree
        # canopy density > self.canpoy_dens
        loss = loss_image.updateMask(
            tree_cover.gte(self.canpoy_dens))

        # Calculate area of loss in hectares for high-density areas
        loss_area = loss.multiply(
            ee.Image.pixelArea().divide(10000))

        # Combine high-density loss area and year into a single image,
        # reduce by region using sum grouped by lossyear
        yearly_loss_area = loss_area.addBands(loss_year).reduceRegion(
            reducer=ee.Reducer.sum().group(1, 'lossyear'),
            geometry=self._buffer_poly,
            scale=30,
            maxPixels=1e9
        )
        return self._format_yearly_data(yearly_loss_area.getInfo())

    @staticmethod
    def _format_yearly_data(data: dict) -> dict:
        """
        Function to convert yearly tree cover loss to format

        Input:
            data (dict): The dictionary containing the total tree cover
            loss by year.
        Output:
            dict: The formatted dictionary containing the year and the
            corresponding tree cover loss area in hectares.

        """

        groups = data['groups']
        formatted_data = {}
        for item in groups:
            year = item['lossyear']
            loss_sum = item['sum']
            formatted_data[f"20{year:02d}"] = loss_sum
        return formatted_data


def create_farm_properties(farm, analyzer):
    """
    Create farm properties based on the given farm object.

    Args:
        farm (Farm): The farm object for which to create properties.

    Returns:
        FarmProperty: The created FarmProperty object.

    Raises:
        None

    """
    
    # Get the FarmProperty model
    FarmPropertyModel = apps.get_model('farms', 'FarmProperty')
    
    # Prepare the data for creating the FarmProperty object
    data = {
        "farm": farm,
        "total_area": analyzer._buffer_poly.area().getInfo()/10000,
        "primary_forest_area": analyzer.calculate_primary_forest(),
        "tree_cover_extent": analyzer.calculate_tree_cover(),
        "protected_area": analyzer.calculate_protected_area()
    }
    
    # Create FarmProperty object
    FarmPropertyModel.objects.update_or_create(farm=farm, defaults=data)
    return True


def create_yearly_tree_cover_loss(farm, analyzer_10, analyzer_30):
    """
    Creates yearly tree cover loss for a given farm.

    Args:
        farm (Farm): The farm object for which the yearly tree cover 
        loss is created.

    Returns:
        list: A list of YearlyTreeCoverLossModel objects created.

    Raises:
        None

    """

    # Calculate yearly tree cover loss for both canopy densities
    year_data_30 = analyzer_30.calculate_yearly_tree_cover_loss()
    year_data_10 = analyzer_10.calculate_yearly_tree_cover_loss()

    # Create loss events for both canopy densities
    for year, value in year_data_30.items():
        YearlyTreeCoverLoss.objects.update_or_create(
            farm=farm, year=year, canopy_density=30, 
            defaults={'value':value}
        )
    for year, value in year_data_10.items():
        YearlyTreeCoverLoss.objects.update_or_create(
            farm=farm, year=year, canopy_density=10, 
            defaults={'value':value}
        )
    
    return True


def calculate_hex_radius(area_in_ha):

    # 1 hectare = 10,000 square meters
    area_in_sqm = area_in_ha * 10000

    # The formula for the area of a regular hexagon is (3 * sqrt(3) / 2) * r^2
    # Solving for r gives r = sqrt((2 * area) / (3 * sqrt(3)))
    radius = math.sqrt((2 * area_in_sqm) / (3 * math.sqrt(3)))
    return radius


def create_hexagon(lat, lon, area_in_ha):

    # Calculate the radius needed for a hexagon with the given area
    radius = calculate_hex_radius(area_in_ha)

    # Set up transformer to convert from lat/lon (WGS84) to UTM (projected)
    transformer_to_utm = Transformer.from_crs(
        "epsg:4326", "epsg:32633", always_xy=True)
    transformer_to_latlon = Transformer.from_crs(
        "epsg:32633", "epsg:4326", always_xy=True)

    # Convert the center lat/lon to UTM
    utm_center = transformer_to_utm.transform(lon, lat)

    # Create the hexagon in UTM coordinates
    hexagon = Polygon([
        (utm_center[0] + radius * math.cos(angle),
         utm_center[1] + radius * math.sin(angle))
        for angle in [math.radians(60 * i) for i in range(6)]
    ])

    # Convert the hexagon back to lat/lon (WGS84)
    hexagon_latlon = transform(transformer_to_latlon.transform, hexagon)
    return hexagon_latlon


def polygon_to_geojson(polygon):
    """Function to convert a polygon to GeoJSON format"""

    geojson = {
        "type": "Feature",
        "geometry": mapping(polygon),
        "properties": {}
    }
    return geojson


def coord_to_poly(latitude, longitude, area_in_ha=.25):
    """Function to change point coordinate to polygon"""

    # Create the hexagon
    hex_polygon = create_hexagon(latitude, longitude, area_in_ha)

    polygon = mapping(hex_polygon)
    return polygon


def calculate_yearly_tree_cover_loss(farm):
    """Calculate yearly tree cover loss of farms"""
    
    if "geometry" in farm.geo_json:
        # Create a ForestAnalyzer object with the farm's geometry
        analyzer_10 = ForestAnalyzer(
            geo_json=farm.geo_json['geometry'], canopy_dens=10)
        analyzer_30 = ForestAnalyzer(geo_json=farm.geo_json['geometry'])
    else:
        raise ValueError("Invalid geo json")
    create_farm_properties(farm, analyzer_30)
    create_yearly_tree_cover_loss(farm, analyzer_10, analyzer_30)
    return


def calculate_all_farms_tree_cover_loss():
    """Calculate tree cover loss for all farms"""

    from v1.farms.models import Farm

    for farm in Farm.objects.all():
        calculate_yearly_tree_cover_loss(farm)
    return