from django.contrib.auth.admin import UserAdmin
from django.contrib import admin

from .models.accounts import User
from .models.batches import Batch
from .models.nodes import SupplyChain
from .models.nodes import Company
from .models.nodes import Farmer

class NavigateUserAdmin(UserAdmin):
    """
    Custom admin class for managing SSO users.
    """
    model = User


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    """
    Admin class for managing batches.
    """
    pass

@admin.register(SupplyChain)
class SupplyChainAdmin(admin.ModelAdmin):
    """
    Admin class for managing supply chains.
    """
    pass

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Admin class for managing companies.
    """
    pass

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    """
    Admin class for managing farmers.
    """
    pass
