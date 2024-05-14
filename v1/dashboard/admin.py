from django.contrib import admin

from .models import Theme
from .models import Intervention

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """
    Admin class for managing Theme model in the Django admin interface.
    """
    pass


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    """
    Admin class for managing Intervention model in the Django admin interface.
    """
    pass