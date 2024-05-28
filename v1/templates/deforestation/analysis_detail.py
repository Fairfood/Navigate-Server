from django.utils.translation import gettext as _
from django.db.models import Count
from django.db.models import Q

from collections import defaultdict

from ...farms.constants import Pillers
from .analysis import Methods

def get_data(queryset):
    queryset = queryset.filter(property__isnull=False)
    data = queryset.annotate(
        comments_count=Count(
            'comments', 
            filter=Q(comments__piller=Pillers.DEFORESTATION)
        )).values_list(
            "external_id", 
            "farmer__supply_chains__name", 
            "property__total_area", 
            "property__tree_cover_extent", 
            "state", 
            "country", 
            "comments_count"
        )
    FarmComment = queryset.model.comments.field.model
    comments_qs = FarmComment.objects.filter(farm__in=queryset, 
                                             piller=Pillers.DEFORESTATION)
    comments = comments_qs.values("farm__external_id", "comment","file",
                                  "source")
    comments_dict = defaultdict(list)

    for comment in comments:
        farm = comment.pop("farm__external_id")
        comments_dict[farm].append(comment)

    return {
        "title": _("Tree cover loss events"),
        "description": _("Tree cover loss events describe the "
                            "reduction of tree canopy due to factors "
                            "like deforestation, natural disasters, "
                            "urban development, and illegal logging. "
                            "This leads to significant environmental "
                            "impacts, including habitat destruction, "
                            "biodiversity loss, and increased carbon "
                            "emissions, affecting both local and "
                            "global climates. Addressing tree cover "
                            "loss is vital for environmental "
                            "conservation and climate change "
                            "mitigation."),
        "table": {
            "methods": Methods.values,
            "head": [
                "Polygon ID",
                "Commodity",
                "Size (Ha)",
                "Tree cove loss (Ha)",
                "Province",
                "Country",
                "Note"
            ],
            "rows": [
                        {
                            "values": items,
                            "comments": comments_dict[items[0]]
                        } for items in data  
                    ],
            }  
    }