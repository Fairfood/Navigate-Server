from django.utils.translation import gettext_lazy as _

def get_data(queryset):
    """
    Get data for deforestation assessment.

    Args:
        queryset: The queryset containing the data for analysis.

    Returns:
        A dictionary containing the title, description, and indexes for the 
        deforestation assessment.

    """
    return {
        "title": _("Deforestation assessment"),
        "description": _(
            "Based on analyzing {polygon_count} polygon areas and Estimates "
            "for overall loss and loss by category (e.g. primary forest, "
            "protected areas) are based on Hansen et al using tree cover "
            "extent from 2000 and Landsat satellite imagery."
        ).format(queryset.count()),
        "indexes": [
            {
                "name": "Number of locations",
                "value": queryset.count()
            },
            {
                "name": "Tree Cover Extent",
                "value": queryset.tree_cover_extent()
            },
            {
                "name": "Primary Forest",
                "value": f"{queryset.primary_forest_area()}%"
            },
            {
                "name": "Protected Area",
                "value": f"{queryset.protected_area()}%"
            },
            {
                "name": "Total Hectares",
                "value": queryset.total_area()
            }
        ]
    }