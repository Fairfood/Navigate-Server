from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models.accounts import User
from .models.analysis import AnalysisQueue
from .models.batches import Batch
from .models.nodes import Company, Farmer, SupplyChain


@admin.register(User)
class NavigateUserAdmin(UserAdmin):
    """
    Custom admin class for managing SSO users.
    """
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ["sso_id"]}),)
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

@admin.register(AnalysisQueue)
class AnalysisQueueAdmin(admin.ModelAdmin):
    """
    Admin class for managing AnalysisQueue.
    """
    pass

