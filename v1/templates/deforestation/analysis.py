from django.db import models
from django.utils.translation import gettext_lazy as _
from v1.farms.constants import TreeCoverLossStandard


def get_data(queryset):
    """
    Retrieves and formats data for the summary of deforestation.
    
    Args:
        queryset: The queryset containing the data to be summarized.

    Returns:
        A dictionary containing the summary of deforestation data. 
    """

    def get_value(key):
        """Helper to handle None values and rounding."""
        return round(key or 0, 2)

    def is_acceptable(values):
        """Helper to check if all values are zero."""
        return 'Acceptable' if all(
            value == 0 for value in values) else 'Not Acceptable'

    rainorest_alliance = queryset.group_summary_by_criteria(
        TreeCoverLossStandard.RAINFOREST_ALLIANCE)
    fairtrade = queryset.group_summary_by_criteria(
        TreeCoverLossStandard.FAIRTRADE)
    eudr = queryset.group_summary_by_criteria(TreeCoverLossStandard.EUDR)

    # Impact evaluation per criteria
    impact_data = {
        'rainorest_alliance': rainorest_alliance,
        'fairtrade': fairtrade,
        'eudr': eudr,
    }

    # Impact status for each method
    impact_status = {
        method: False if data['sum'] else True
        for method, data in impact_data.items()
    }

    # Overall impact evaluation (if all methods are impacted)
    overall_impact = all(impact_status.values())

    # Response Data
    response = {
        "title": _("Summary of deforestation"),
        "description": _("Tradin employs risk assessment criteria that include"
                         " a 113-meter radius for tree cover loss evaluation "
                         "around farms, and a 2-kilometer proximity measure "
                         "for special forests or protected areas, adhering to "
                         "EUDR and Rainforest Alliance standards."),
        "head": [
            {"id": 1, "name": "Criteria"},
            {"id": 2, "name": "Status"},
            {"id": 3, "name": TreeCoverLossStandard.RAINFOREST_ALLIANCE.label,
             "info": _("Monitoring tree cover loss in regions with a canopy "
                       "density of 10% or higher, spanning from 2014 to "
                       "present. All instances of even minimal canopy loss "
                       "are considered unacceptable.")},
            {"id": 4, "name": TreeCoverLossStandard.FAIRTRADE.label,
             "info": _("Monitoring tree cover loss in regions with a canopy "
                       "density of 10% or higher, spanning from 2019 to "
                       "the present. All instances of even minimal canopy "
                       "loss are considered unacceptable.")},
            {"id": 5, "name": TreeCoverLossStandard.EUDR.label,
             "info": _("Monitoring tree cover loss in regions with a canopy "
                       "density of 30% or higher, spanning from 2020 to "
                       "the present. All instances of even minimal canopy "
                       "loss are considered unacceptable.")}
        ],
        "rows": [
            {
                "id": 1,
                "values": [
                    "Tree cover loss area",
                    is_acceptable(
                        [rainorest_alliance['sum'], fairtrade['sum'], 
                        eudr['sum']]),
                    get_value(rainorest_alliance['sum']),
                    get_value(fairtrade['sum']),
                    get_value(eudr['sum'])
                ]
            },
            {
                "id": 2,
                "values": [
                    "Tree cover loss events",
                    is_acceptable(
                        [rainorest_alliance['count'], fairtrade['count'], 
                         eudr['count']]),
                    get_value(rainorest_alliance['count']),
                    get_value(fairtrade['count']),
                    get_value(eudr['count'])
                ]
            },
            {
                "id": 3,
                "values": [
                    "Forest loss in protected area event",
                    "Acceptable", 0, 0, 0,
                ]
            }
        ]
    }

    # Impact structure
    impact = [
        {
            "name": "Overall",
            "is_passed": overall_impact,
            "indexes": [
                {
                    "name": "Total tree area lost", 
                    "is_passed": overall_impact
                },
                {
                    "name": "Deforestation event count", 
                    "is_passed": overall_impact
                },
                {
                    "name": "Deforestation event share", 
                    "is_passed": overall_impact
                }
            ]
        }
    ]

    for method in impact_data:
        name = method.replace("_", " ").title()
        if name == "Eudr":
            name = name.upper()   
        impact.append({
            "name": name,
            "is_passed": impact_status[method],
            "indexes": [
                {
                    "name": "Total tree area lost", 
                    "is_passed": impact_status[method]
                },
                {
                    "name": "Deforestation event count", 
                    "is_passed": impact_status[method]
                },
                {
                    "name": "Deforestation event share", 
                    "is_passed": impact_status[method]
                }
            ]
        })

    return {
        "impact": impact,
        "analysis": response
    }
