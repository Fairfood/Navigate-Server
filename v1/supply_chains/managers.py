from django.db import models

class BatchQuerySet(models.QuerySet):
    """
    A custom QuerySet class for batch queries.

    This class provides methods to filter the queryset based on query 
    parameters and keyword arguments.

    Example usage:
        queryset = BatchQuerySet(model).filter_by_request(request)

    Attributes:
        model: The model associated with the queryset.
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
        
    

