import os
import json
from faker import Faker
from functools import lru_cache

from django.conf import settings
from django.apps import apps

from v1.farms.constants import Pillers


COMPANY_ID = "VkDVYQe"
faker = Faker()

def load_geo_json():
    file_path = os.path.join(settings.BASE_DIR, 'scripts', 'tradin250.geojson')

    with open(file_path, 'r') as geojson_file:
        return json.load(geojson_file)

# @lru_cache
def get_company():
    CompanyModel = apps.get_model('supply_chains', 'Company')
    try:
        return CompanyModel.objects.get(id=COMPANY_ID)
    except CompanyModel.DoesNotExist:
        raise Exception("Check if the company exists in the database")
    
def create_farmer():
    FarmerModel = apps.get_model('supply_chains', 'Farmer')
    data = {
        "country": "Sierra Leone",
        "state": "Western Area",
        "city": "Freetown",
        "external_id": faker.uuid4(),
        "name": faker.name(),
        "company": get_company()
    }
    return FarmerModel.objects.create(**data)

def create_farm(farmer, geo_json):
    FarmModel = apps.get_model('farms', 'Farm')
    data = {
        "external_id": faker.uuid4(),
        "farmer": farmer,
        "analysis_radius": 30,
        "geo_json": geo_json
    }
    return FarmModel.objects.create(**data)

def create_farm_properties(farm):
    FarmPropertyModel = apps.get_model('farms', 'FarmProperty')
    data = {
        "farm": farm,
        "total_area": faker.random_int(10, 100),
        "primary_forest_area": faker.random_int(1, 10),
        "tree_cover_extent": faker.random_int(1, 10),
        "protected_area": faker.random_int(1, 10)
    }
    return FarmPropertyModel.objects.create(**data)

def create_farm_comment(farm):
    FarmCommentModel = apps.get_model('farms', 'FarmComment')
    data = {
        "farm": farm,
        "comment": faker.text(),
        "source": faker.company(),
        "piller": Pillers.DEFORESTATION
    }
    return FarmCommentModel.objects.create(**data)

def create_batch():
    BatchModel = apps.get_model('supply_chains', 'Batch')
    data = {
        "external_id": faker.uuid4(),
        "supply_chain": get_company().supply_chains.last(),
    }
    return BatchModel.objects.create(**data)

def create_deforestation_summery(farm):
    DeforestationSummaryModel = apps.get_model(
        'farms', 'DeforestationSummary')
    data = [
                {
                    "farm": farm,
                    "name": "Tree cover loss events",
                    "year": faker.random_int(2014, 2024),
                    "canopy_density": faker.random_int(10, 100),
                    "source": faker.company(),
                    "value": 1
                },
                {
                    "farm": farm,
                    "name": "Tree cover loss events",
                    "year": faker.random_int(2014, 2024),
                    "canopy_density": faker.random_int(10, 100),
                    "source": faker.company(),
                    "value": 1
                },
                {
                    "farm": farm,
                    "name": "Tree cover loss events",
                    "year": faker.random_int(2014, 2024),
                    "canopy_density": faker.random_int(10, 100),
                    "source": faker.company(),
                    "value": 1
                },
                {
                    "farm": farm,
                    "name": "Tree cover loss area",
                    "year": faker.random_int(2014, 2024),
                    "canopy_density": faker.random_int(10, 100),
                    "source": faker.company(),
                    "value": 0.5329 
                },
                {
                    "farm": farm,
                    "name": "Tree cover loss area",
                    "year": faker.random_int(2014, 2024),
                    "canopy_density": faker.random_int(10, 100),
                    "source": faker.company(),
                    "value": 0.5329 
                },
                {
                    "farm": farm,
                    "name": "Tree cover loss area",
                    "year": faker.random_int(2014, 2024),
                    "canopy_density": faker.random_int(10, 100),
                    "source": faker.company(),
                    "value": 0.5329 
                },
                {
                    "farm": farm,
                    "name": "Forest loss in protected area event",
                    "year": faker.random_int(2014, 2024),
                    "canopy_density": faker.random_int(10, 100),
                    "source": faker.company(),
                    "value": 1
                },
                {
                    "farm": farm,
                    "name": "Forest loss in protected area event",
                    "year": faker.random_int(2014, 2024),
                    "canopy_density": faker.random_int(10, 100),
                    "source": faker.company(),
                    "value": 1
                },
                {
                    "farm": farm,
                    "name": "Forest loss in protected area event",
                    "year": faker.random_int(2014, 2024),
                    "canopy_density": faker.random_int(10, 100),
                    "source": faker.company(),
                    "value": 1
                },
                {
                    "farm": farm,
                    "name": "Forest loss in protected area event",
                    "year": faker.random_int(2014, 2024),
                    "canopy_density": faker.random_int(10, 100),
                    "source": faker.company(),
                    "value": 1
                },
            ]
    summary = []
    for i in data:
        summary.append(DeforestationSummaryModel(**i))
    return DeforestationSummaryModel.objects.bulk_create(summary)

def load_tradin_data():
    company = get_company()
    batch = create_batch()
    supply_chain = company.supply_chains.last()
    geo_json = load_geo_json()
    
    for obj in geo_json['features']:
        farmer = create_farmer()
        farmer.add_supply_chain(supply_chain)
        farm = create_farm(farmer)
        create_farm_properties(farm)
        create_farm_comment(farm)
        create_deforestation_summery(farm)
        batch.farmers.add(farmer)
    print("Data loaded successfully")



        
