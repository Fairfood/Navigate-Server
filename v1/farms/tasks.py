import time
from contextlib import contextmanager
from hashlib import md5
from typing import Union

from celery import shared_task
from django.apps import apps
from django.core.cache import cache
from sentry_sdk import capture_exception, capture_message

from v1.farms.earth_engine import ForestAnalyzer
from v1.farms.models import Farm, YearlyTreeCoverLoss, FarmProperty
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
    
    farm = Farm.objects.filter(id=farm_id).first()
    if farm:
        # Check if the farm has a geometry field
        if "geometry" in farm.geo_json:
            # Create a ForestAnalyzer object with the farm's geometry
            analyzer = ForestAnalyzer(
                geo_json=farm.geo_json["geometry"], canopy_dens=10)
        else:
            raise ValueError("Invalid geo json")

        # Prepare the data for creating the FarmProperty object
        data = {
            "farm": farm,
            "total_area": analyzer.calculate_area(farm.geo_json['geometry']),
            "primary_forest_area": analyzer.calculate_primary_forest(),
            "tree_cover_extent": analyzer.calculate_tree_cover(),
            "protected_area": analyzer.calculate_protected_area()
        }
        
        # Create FarmProperty object
        FarmProperty.objects.update_or_create(farm=farm, defaults=data)
        return True


@shared_task(name="create_yearly_tree_cover_loss")
def create_yearly_tree_cover_loss(farm_id: Union[int, None] = None):
    """
    Creates yearly tree cover loss for a given farm.

    Args:
        farm (Farm): The farm object for which the yearly tree cover loss 
        is created.

    Returns:
        list: A list of YearlyTreeCoverLoss objects created.
    """

    farm = Farm.objects.filter(id=farm_id).first()
    if farm:
        # Check if the farm has a geometry field
        if "geometry" in farm.geo_json:
            # Create a ForestAnalyzer object with the farm's geometry
            analyzer_10 = ForestAnalyzer(
                geo_json=farm.geo_json['geometry'], canopy_dens=10)
            analyzer_30 = ForestAnalyzer(geo_json=farm.geo_json['geometry'])
        else:
            raise ValueError("Invalid geo json")

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
            # capture_message(f"Driver ID syncing started in 
            # {settings.ENVIRONMENT}")
            sync_ids = AnalysisQueue.objects.filter(
                status=suply_constants.SyncStatus.IN_QUEUE
            ).values_list("farm__id", "id")
            for farm_id, id in sync_ids:
                AnalysisQueue.objects.filter(id=id).update(
                    status=suply_constants.SyncStatus.STARTED)
                try:
                    if farm_id:
                        create_farm_properties(farm_id)
                        create_yearly_tree_cover_loss(farm_id)
                    AnalysisQueue.objects.filter(id=id).update(
                        status=suply_constants.SyncStatus.COMPLETED)
                except Exception as e:
                    capture_exception(e)
                    AnalysisQueue.objects.filter(id=id).update(
                        status=suply_constants.SyncStatus.FAILED)

            return True
        else:
            capture_message(
                f"{self.__name__} : Celery waiting for the previous task to \
                be complete.")
