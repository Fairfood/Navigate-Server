from django.db import models
from django.db.models import Sum, Avg, Count, FloatField
from django.db.models.functions import Coalesce, Cast
from v1.farms.constants import TreeCoverLossStandard


FarmFilter = {
    TreeCoverLossStandard.RAINFOREST_ALLIANCE: {
        "year__gte": 2014,
        "canopy_density": 10,
    },
    TreeCoverLossStandard.FAIRTRADE: {
        "year__gte": 2019,
        "canopy_density": 10,
    },
    TreeCoverLossStandard.EUDR: {
        "year__gte": 2020,
        "canopy_density": 30,
    },
}

class FarmQuerySet(models.QuerySet):
    """
    A custom QuerySet for the Farm model.

    This QuerySet provides additional methods for annotating farms with various 
    calculated fields.
    """

    def calc_percentage(self, num, denum):
        if denum == 0:
            return 0
        percen = round((num * 100 / denum), 2)
        if percen > 100:
            return 100
        return percen

    def total_area(self):
        """
        Annotates farms with the total area of their properties.

        Returns:
        QuerySet: A QuerySet of farms annotated with the 'total_area' field.
        """
        return self.aggregate(
            total_area=Sum('property__total_area'))["total_area"]

    def primary_forest_area(self):
        """
        Annotates farms with the average primary forest area of their 
        properties.

        Returns:
        QuerySet: A QuerySet of farms annotated with the 'primary_forest_area' 
            field.
        """
        primary_forest = self.aggregate(
            primary_forest_area=Sum('property__primary_forest_area')
        )["primary_forest_area"] or 0
        total_area = self.total_area() or 0
        return self.calc_percentage(primary_forest, total_area)
    
    def tree_cover_extent(self):
        """
        Annotates farms with the average tree cover extent of their properties.

        Returns:
        QuerySet: A QuerySet of farms annotated with the 'tree_cover_extent' 
            field.
        """
        tree_cover = self.aggregate(
            tree_cover_extent=Sum('property__tree_cover_extent')
        )["tree_cover_extent"] or 0
        total_area = self.total_area() or 0
        return self.calc_percentage(tree_cover, total_area)
    
    def protected_area(self):
        """
        Annotates farms with the average protected area of their properties.

        Returns:
        QuerySet: A QuerySet of farms annotated with the 'protected_area' 
            field.
        """
        return self.aggregate(
            protected_area=Sum('property__protected_area')
            )["protected_area"]
    
    def group_summary_by_criteria(self, method):
        """
        Groups the deforestation summary by a given criteria.

        Args:
            method (str): The criteria to group the deforestation summary by.

        Returns:
            QuerySet: A queryset containing the grouped deforestation summary.

        Example:
            >>> group_summary_by_criteria('method_name')
            <QuerySet [{'name': 'criteria_name', 'value': 123}, ...]>
        """
        YearlyTreeCoverLoss = self.model.yearly_tree_cover_losses.field.model
        queryset = YearlyTreeCoverLoss.objects.filter(
            farm__in=self, **FarmFilter[method])
        return queryset.aggregate(
            sum=Coalesce(Cast(Sum('value'), output_field=FloatField()), 0.0),
            count=Count('value')
        )
    
    def filter_by_request(self, request):
        """
        Filters the data based on the query parameters in the request.

        Args:
            request: The request object containing the query parameters.

        Returns:
            The filtered data based on the query parameters.
        """
        data = request.query_params
        return self.filter_by_kwargs(data)

    def filter_by_kwargs(self, kwargs):
        """
        Filter the queryset based on the provided keyword arguments.

        Args:
            **kwargs: Keyword arguments to filter the queryset.

        Returns:
            QuerySet: The filtered queryset.
        """
        country = kwargs.get('country')
        _state = kwargs.get('state')
        farmer = kwargs.get('farmer')
        company = kwargs.get('company')
        supply_chain = kwargs.get('supply_chain')
        criteria = kwargs.get('criteria')
        method = kwargs.get('method')
        batch = kwargs.get('batch')

        if country:
            self = self.filter(country=country)
        if batch:
            self = self.filter(farmer__batches__id=batch).distinct()
        if _state:
            self = self.filter(state=_state)
        if farmer:
            self = self.filter(farmer_id=farmer)
        if company:
            self = self.filter(farmer__company_id=company)
        if supply_chain:
            self = self.filter(farmer__supply_chains__id=supply_chain)

        # YearlyTreeCoverLoss = self.model.yearly_tree_cover_losses.field.model
        # queryset = YearlyTreeCoverLoss.objects.filter(
        #     farm__in=self)
        # self = self.filter(yearly_tree_cover_losses__in=queryset)
        
        # if method and method in FarmFilter:
        #     queryset = queryset.filter(**FarmFilter[method])
        #     self = self.filter(yearly_tree_cover_losses__in=queryset)
        return self
        
class FarmCommentQuerySet(models.QuerySet):
    """
    Custom QuerySet for filtering farm comments based on query parameters.
    """

    def filter_by_request(self, request):
        """
        Filters the data based on the query parameters in the request.

        Args:
            request: The request object containing the query parameters.

        Returns:
            The filtered data based on the query parameters.
        """
        data = request.query_params
        return self.filter_by_kwargs(**data)

    def filter_by_kwargs(self, **kwargs):
        """
        Filter the queryset based on the provided keyword arguments.

        Args:
            **kwargs: Keyword arguments to filter the queryset.

        Returns:
            QuerySet: The filtered queryset.
        """
        farm = kwargs.get('farm')
        piller = kwargs.get('piller')

        if farm:
            self = self.filter(farm_id=farm)
        if piller:
            self = self.filter(piller=piller)
        return self
        
    

