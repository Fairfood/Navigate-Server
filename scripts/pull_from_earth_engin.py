import ee
from django.apps import apps
ee.Initialize()

# Define the polygon coordinates for the analysis


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
        print('Initing analyzer')
        if geo_json["type"] == "Point":
            self.polygon = ee.Geometry.Point(geo_json["coordinates"])
        elif geo_json["type"] == "Polygon":
            self.polygon = ee.Geometry.Polygon(geo_json["coordinates"][0])
        else:
            raise ValueError("Invalid geojson data, Only Point and Polygon are supported.")
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
        Calculates the total tree cover loss for each year within the specified polygon.
        This function processes the 'lossyear' band from the dataset to determine the year of tree cover loss,
        creates a binary mask to indicate areas of loss, and sums up the area of loss for each year.
        The areas of loss are converted from square meters to hectares .

        Returns:
            list of dict: Each dictionary contains the year and the corresponding tree cover loss area in hectares.
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


# analyzer = ForestAnalyzer(polygon=polygon_cords[0], canopy_dens=30)
# print(analyzer.calculate_yearly_tree_cover_loss())

def create_farm_properties(farm):
    """
    Create farm properties based on the given farm object.

    Args:
        farm (Farm): The farm object for which to create properties.

    Returns:
        FarmProperty: The created FarmProperty object.

    Raises:
        None

    """
    # Check if the farm has a geometry field
    if "geometry" in farm.geo_json:
        # Create a ForestAnalyzer object with the farm's geometry
        analyzer = ForestAnalyzer(geo_json=farm.geo_json["geometry"], 
                                  canopy_dens=30, buffer_area=30)
    else:
        # Create a ForestAnalyzer object with the farm's geo_json
        analyzer = ForestAnalyzer(geo_json=farm.geo_json, canopy_dens=30, buffer_area=30)
    
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
    
    # Create and return the FarmProperty object
    return FarmPropertyModel.objects.create(**data)

def create_deforestation_summery(farm):
    """
    Creates deforestation summary for a given farm.

    Args:
        farm (Farm): The farm object for which the deforestation summary is created.

    Returns:
        list: A list of DeforestationSummaryModel objects created.

    Raises:
        None

    """
    DeforestationSummaryModel = apps.get_model(
        'farms', 'DeforestationSummary')
    
    # Check if the farm has a geometry field
    if "geometry" in farm.geo_json:
        analyzer_30 = ForestAnalyzer(geo_json=farm.geo_json["geometry"], 
                                  canopy_dens=30, buffer_area=30)
    else:
        analyzer_10 = ForestAnalyzer(geo_json=farm.geo_json, canopy_dens=30)

    # Calculate yearly tree cover loss for both canopy densities
    year_data_30 = analyzer_30.calculate_yearly_tree_cover_loss()
    year_data_10 = analyzer_10.calculate_yearly_tree_cover_loss()

    # Create loss events for canopy density 30
    loss_events = [
        {
            "farm": farm,
            "name": "Tree cover loss events",
            "year": year,
            "canopy_density": 30,
            "source": "Global Forest Change",
            "value": 1
        } for year, _ in year_data_30.items()
    ]

    # Create loss area for canopy density 30
    loss_area = [
        {
            "farm": farm,
            "name": "Tree cover loss area",
            "year": year,
            "canopy_density": 30,
            "source": "Global Forest Change",
            "value": value
        } for year, value in year_data_30.items()
    ]

    # Create loss events for canopy density 10
    loss_events = loss_events + [
        {
            "farm": farm,
            "name": "Tree cover loss events",
            "year": year,
            "canopy_density": 10,
            "source": "Global Forest Change",
            "value": 1
        } for year in year_data_10.items()
    ]

    # Create loss area for canopy density 10
    loss_area = loss_area + [
        {
            "farm": farm,
            "name": "Tree cover loss area",
            "year": year,
            "canopy_density": 10,
            "source": "Global Forest Change",
            "value": value
        } for year, value in year_data_10.items()
    ]

    # Check if there is protected area loss
    protected_loss =  1 if analyzer_10.calculate_protected_area() > 0 else 0

    # Create forest loss events for specific years
    forest_loss = [
        {
            "farm": farm,
            "name": "Tree cover loss area",
            "year": 2014,
            "canopy_density": 30,
            "source": "Global Forest Change",
            "value": protected_loss
        },{
            "farm": farm,
            "name": "Tree cover loss area",
            "year": 2019,
            "canopy_density": 30,
            "source": "Global Forest Change",
            "value": protected_loss
        } ,{
            "farm": farm,
            "name": "Tree cover loss area",
            "year": 2020,
            "canopy_density": 10,
            "source": "Global Forest Change",
            "value": protected_loss
        } 
    ]

    # Combine all the data
    data = loss_events + loss_area + forest_loss

    # Create DeforestationSummaryModel objects
    summary = []
    for i in data:
        summary.append(DeforestationSummaryModel(**i))
    # print(summary[0])
    # Bulk create the DeforestationSummaryModel objects
    return DeforestationSummaryModel.objects.bulk_create(summary)