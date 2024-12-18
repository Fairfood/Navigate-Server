import time
from contextlib import contextmanager
from hashlib import md5
from typing import Union

from celery import shared_task
from django.apps import apps
from django.core.cache import cache
from sentry_sdk import capture_exception, capture_message

from v1.farms.earth_engine import ForestAnalyzer
from v1.farms.models import Farm
from v1.supply_chains import constants as suply_constants
from v1.supply_chains.models.analysis import AnalysisQueue

LOCK_EXPIRE = 60 * 60 * 24  # Lock expires in 1 day

@shared_task(name="create_farm_properties")
def create_farm_properties(farm_id: Union[int, None] = None):
    """
    Create farm properties based on the given farm object.

    Args:
        farm_id (Union[int, None], optional): The farm object id for which to create properties.

    Raises:
        None

    """
    if not farm_id:
        return
    farm = Farm.objects.filter(id=farm_id).first()
    if farm:
        # Check if the farm has a geometry field
        if "geometry" in farm.geo_json:
            # Create a ForestAnalyzer object with the farm's geometry
            analyzer = ForestAnalyzer(
                geo_json=farm.geo_json["geometry"], canopy_dens=30, buffer_area=30
            )
        else:
            # Create a ForestAnalyzer object with the farm's geo_json
            analyzer = ForestAnalyzer(
                geo_json=farm.geo_json, canopy_dens=30, buffer_area=30
            )

        # Get the FarmProperty model
        FarmPropertyModel = apps.get_model("farms", "FarmProperty")

        # Prepare the data for creating the FarmProperty object
        data = {
            "farm": farm,
            "total_area": analyzer._buffer_poly.area().getInfo() / 10000,
            "primary_forest_area": analyzer.calculate_primary_forest(),
            "tree_cover_extent": analyzer.calculate_tree_cover(),
            "protected_area": analyzer.calculate_protected_area(),
        }

        # Create  the FarmProperty Id
        FarmPropertyModel.objects.create(**data)


@shared_task(name="create_deforestation_summery")
def create_deforestation_summery(farm_id: Union[int, None] = None):
    """
    Creates deforestation summary for a given farm.

    Args:
        farm (Farm): The farm object for which the deforestation summary is created.

    Returns:
        list: A list of DeforestationSummaryModel objects created.

    Raises:
        None

    """
    if not farm_id:
        return
    farm = Farm.objects.filter(id=farm_id).first()
    if farm:
        DeforestationSummaryModel = apps.get_model("farms", "DeforestationSummary")

        # Check if the farm has a geometry field
        if "geometry" in farm.geo_json:
            analyzer_30 = ForestAnalyzer(
                geo_json=farm.geo_json["geometry"], canopy_dens=30, buffer_area=30
            )
        else:
            analyzer_10 = ForestAnalyzer(geo_json=farm.geo_json, canopy_dens=30) # 2 um venam

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
                "value": 1,
            }
            for year, _ in year_data_30.items()
        ]

        # Create loss area for canopy density 30
        loss_area = [
            {
                "farm": farm,
                "name": "Tree cover loss area",
                "year": year,
                "canopy_density": 30,
                "source": "Global Forest Change",
                "value": value,
            }
            for year, value in year_data_30.items()
        ]

        # Create loss events for canopy density 10
        loss_events = loss_events + [
            {
                "farm": farm,
                "name": "Tree cover loss events",
                "year": year,
                "canopy_density": 10,
                "source": "Global Forest Change",
                "value": 1,
            }
            for year in year_data_10.items()
        ]

        # Create loss area for canopy density 10
        loss_area = loss_area + [
            {
                "farm": farm,
                "name": "Tree cover loss area",
                "year": year,
                "canopy_density": 10,
                "source": "Global Forest Change",
                "value": value,
            }
            for year, value in year_data_10.items()
        ]

        # Check if there is protected area loss
        protected_loss = 1 if analyzer_10.calculate_protected_area() > 0 else 0

        # Create forest loss events for specific years
        forest_loss = [
            {
                "farm": farm,
                "name": "Tree cover loss area",
                "year": 2014,
                "canopy_density": 30,
                "source": "Global Forest Change",
                "value": protected_loss,
            },
            {
                "farm": farm,
                "name": "Tree cover loss area",
                "year": 2019,
                "canopy_density": 30,
                "source": "Global Forest Change",
                "value": protected_loss,
            },
            {
                "farm": farm,
                "name": "Tree cover loss area",
                "year": 2020,
                "canopy_density": 10,
                "source": "Global Forest Change",
                "value": protected_loss,
            },
        ]

        # Combine all the data
        data = loss_events + loss_area + forest_loss

        # Create DeforestationSummaryModel objects
        summary = []
        for i in data:
            summary.append(DeforestationSummaryModel(**i))
        # Bulk create the DeforestationSummaryModel objects
        DeforestationSummaryModel.objects.bulk_create(summary)


@contextmanager
def celery_task_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # cache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


@shared_task(bind=True, name="daily_analysis_sync")
def analysis_sync(self):
    hexdigest = md5(self.__name__.encode("utf-8")).hexdigest()
    lock_id = "{0}-lock".format(hexdigest)
    with celery_task_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            # capture_message(f"Driver ID syncing started in {settings.ENVIRONMENT}")
            sync_ids = AnalysisQueue.objects.filter(status=suply_constants.SyncStatus.IN_QUEUE).values_list("farm__id", "id")
            for farm_id, id in sync_ids:
                AnalysisQueue.objects.filter(id=id).update(status=suply_constants.SyncStatus.STARTED)
                try:
                    create_farm_properties(farm_id)
                    create_deforestation_summery(farm_id)
                    AnalysisQueue.objects.filter(id=id).update(status=suply_constants.SyncStatus.COMPLETED)
                except Exception as e:
                    capture_exception(e)
                    AnalysisQueue.objects.filter(id=id).update(status=suply_constants.SyncStatus.FAILED)

            return True
        else:
            capture_message(f"{self.__name__} : Celery waiting for the previous task to be complete.")
