from django.db import models
from django.utils.translation import gettext_lazy as _


Methods = models.TextChoices('Methods', 'RAINFOREST_ALLIENCE FAIRTRADE EUDR')


def format_data(r, f, e):
    """
    Formats the data by creating a dictionary to store values for each name,
    iterating over the input lists to populate the dictionary, and converting
    the dictionary to the desired format.

    Args:
        r (list): List of dictionaries containing data for 'r'.
        f (list): List of dictionaries containing data for 'f'.
        e (list): List of dictionaries containing data for 'e'.

    Returns:
        list: A list of lists, where each inner list contains the name followed
        by the corresponding values from the input lists.
    """
    # Create a dictionary to store values for each name
    data = {}

    # Iterate over v1 and v2 to populate the dictionary
    for d in r, f , e:
        name = d['name']
        value = d['value']
        if name not in data:
            data[name] = [value]
        else:
            data[name].append(value)

    # Convert the dictionary to the desired format
    return [[name] + values for name, values in data.items()]



def get_data(queryset):
    """
    Retrieves and formats data for the summary of deforestation.

    Args:
        queryset: The queryset containing the data to be summarized.

    Returns:
        A dictionary containing the summary of deforestation data. 
        The dictionary has the following keys:
        - "title": A string representing the title of the summary.
        - "description": A string representing the description of the summary.
        - "head": A list of dictionaries representing the column headers of the 
            summary.
        - "rows": A list of dictionaries representing the rows of the summary.

    """
    rainorest_allience = queryset.group_summary_by_criteria(
        Methods.RAINFOREST_ALLIENCE)
    fairtrade = queryset.group_summary_by_criteria(Methods.FAIRTRADE)
    eudr = queryset.group_summary_by_criteria(Methods.EUDR)

    data = format_data(rainorest_allience, fairtrade, eudr)

    return {
        "title": _("Summary of deforestation"),
        "description": _("Tradin employs risk assessment criteria that include"
                         " a 113-meter radius for tree cover loss evaluation "
                         "around farms, and a 2-kilometer proximity measure "
                         "for special forests or protected areas, adhering to "
                         "EUDR and Rainforest Alliance standards."),
        "head": [
            {
                "id": 1,
                "name": "Criteria"
            },
            {
                "id": 2,
                "name": Methods.RAINFOREST_ALLIENCE,
                "info": _("Monitoring tree cover loss in regions with a canopy"
                          " density of 10% or higher, spanning from 2014 to "
                          "present. All instances of even minimal canopy loss "
                          "are considered unacceptable."),
                
            },
            {
                "id": 3,
                "name": Methods.FAIRTRADE,
                "info": _("Monitoring tree cover loss in regions with a canopy"
                          " density of 10% or higher, spanning from 2019 to "
                          "the present. All instances of even minimal canopy "
                          "loss are considered unacceptable.")
            },
            {
                "id": 4,
                "name": Methods.EUDR,
                "info": _("Monitoring tree cover loss in regions with a canopy"
                          " density of 30% or higher, spanning from 2020 to "
                          "the present. All instances of even minimal canopy "
                          "loss are considered unacceptable.")
            }
        ],
        "rows": [
            {
                "id": 1,
                "values": data[0]
            },
            {
                "id": 2,
                "values": data[1],
            },
            {
                "id": 3,
                "values": data[2],
            }
        ]
    }