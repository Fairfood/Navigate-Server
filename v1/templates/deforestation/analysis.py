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
    
    single_list = []
    for i in [r, f, e]:
        single_list.extend(list(i))

    # Iterate over v1 and v2 to populate the dictionary
    for d in single_list:
        name = d['name']
        value = round(d['value'], 2)
        if name not in data:
            data[name] = [value]
        else:
            data[name].append(value)

    # Convert the dictionary to the desired format
    data_list = [[name] + values for name, values in data.items()]

    for sublist in data_list:
        sublist.extend([0] * (4 - len(sublist)))

    return data_list

def add_unit(data):
    """
    Adds the unit 'ha' to the elements in the given data list, except for the 
    first element in each sublist.

    Parameters:
    data (list): A list of sublists, where each sublist represents a 
    data entry.
    """
    for sublist in data:
        if not sublist[0].endswith("event"):
            for i in range(1, len(sublist)):
                sublist[i] = f"{sublist[i]} ha"

def impact(data):
    """
    Calculates the impact of deforestation based on the given data.

    Args:
        data (list): A 2D list representing the deforestation data.

    Returns:
        list: A 2D list representing the impact of deforestation.
    """
    bool_data = [[bool(value) for value in sublist] for sublist in data]
    overall = [all(col) for col in zip(*bool_data)]
    result = [[all(overall)] + overall]
    for sublist in data:
        result.append([all(sublist)] + sublist)
    return result


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
    impact_data = impact(data)

    add_unit(data)

    response  = {
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
        "rows": []
    }

    for c, item in enumerate(data):
        response["rows"].append( 
            {
                "id": c + 1,
                "values": item
            })
    
    impact_names = ["Overall", "Rainforest Alliance", "Fairtrade", "EUDR"]
    
    return {
        "impact": [
        {
            "name": impact_names[name_index],
            "is_passed" : values[0],
            "indexes": [
                {
                    "name": "Total tree area lost",
                    "is_passed": values[1]
                },
                {
                    "name": "Deforesation event count",
                    "is_passed": values[2]
                },
                {
                    "name": "Deforesation event share",
                    "is_passed": values[3]
                }
            ]
        } for name_index, values in enumerate(impact_data)
    ],
    "analysis": response
    }