from django.contrib import admin
from django.forms import ModelForm
from django.forms.widgets import TextInput

from .models import Theme
from .models import Intervention

class ThemeForm(ModelForm):
    """
    A form for creating or updating a Theme object.

    Inherits from ModelForm class.

    Attributes:
        Meta (class): Inner class that defines metadata options for the form.

    """
    class Meta:
        model = Theme
        fields = '__all__'
        widgets = {
            'primary_color': TextInput(attrs={'type': 'color'}),
            'primary_light_color': TextInput(attrs={'type': 'color'}),
            'secondary_color': TextInput(attrs={'type': 'color'}),
            'stroke_color': TextInput(attrs={'type': 'color'}),
            'first_font_color': TextInput(attrs={'type': 'color'}),
            'second_font_color': TextInput(attrs={'type': 'color'}),
            'third_font_color': TextInput(attrs={'type': 'color'}),
            'info_color': TextInput(attrs={'type': 'color'}),
            'badge_color': TextInput(attrs={'type': 'color'}),
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