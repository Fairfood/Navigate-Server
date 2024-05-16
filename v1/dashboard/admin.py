from django.contrib import admin
from django.forms import ModelForm
from django.forms.widgets import TextInput

from .models import Theme
from .models import Intervention

class ThemeForm(ModelForm):
    class Meta:
        model = Theme
        fields = '__all__'
        widgets = {
            'primary_color': TextInput(attrs={'type': 'color'}),
        }

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    """
    Admin class for managing Theme model in the Django admin interface.
    """
    form = ThemeForm


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    """
    Admin class for managing Intervention model in the Django admin interface.
    """
    pass