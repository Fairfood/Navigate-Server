from django.utils.translation import gettext as _
from django.db.models import Count
from django.db.models import Q, Sum

from collections import defaultdict

from ...farms.constants import Pillers
from .analysis import Methods
from v1.farms import models as farm_models


def round_off(value):
    if type(value) == float:
        value = round(value, 2)
    return value

def get_data(queryset, method):
    tree_cover_losses = farm_models.YearlyTreeCoverLoss.objects.filter(
        farm__in=queryset)
    from v1.farms.managers import FarmFilter
    if method and method in FarmFilter:
        tree_cover_losses = tree_cover_losses.filter(**FarmFilter[method])
    queryset = queryset.filter(
        property__isnull=False, 
        yearly_tree_cover_losses__in=tree_cover_losses)
    data = queryset.annotate(
        comments_count=Count(
            'comments', 
            filter=Q(comments__piller=Pillers.DEFORESTATION)
        ),
        tree_cover_loss_sum=Sum('yearly_tree_cover_losses__value')
    ).values_list(
        "external_id", 
        "farmer__supply_chains__name", 
        "property__total_area",
        "tree_cover_loss_sum",
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
            "methods": ["RAINFOREST ALLIANCE", "FAIRTRADE", "EUDR"],
            "head": [
                "Polygon ID",
                "Commodity",
                "Size (Ha)",
                "Tree cover loss (Ha)",
                "Province",
                "Country",
                "Note"
            ],
            "rows": [
                        {
                            "values": [round_off(item) for item in items],
                            "comments": comments_dict[items[0]]
                        } for items in data  
                    ],
            }  
    }
