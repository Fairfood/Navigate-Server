from django.contrib import admin

from .models import Farm
from .models import FarmProperty
from .models import FarmComment
from .models import DeforestationSummary

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    """
    Admin class for managing the Farm model in the Django admin interface.
    """
    pass

@admin.register(FarmProperty)
class FarmPropertyAdmin(admin.ModelAdmin):
    """
    Admin class for managing the FarmProperty model in the Django admin 
    interface.
    """
    pass

@admin.register(FarmComment)
class FarmCommentAdmin(admin.ModelAdmin):
    """
    Admin class for managing the FarmComment model in the Django admin 
    interface.
    """
    pass

@admin.register(DeforestationSummary)
class DeforestationSummaryAdmin(admin.ModelAdmin):
    """
    Admin class for managing the DeforestationSummary model in the Django 
    admin interface.
    """
    pass