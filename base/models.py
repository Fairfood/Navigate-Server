from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from hashid_field import HashidAutoField


class AbstractBaseModel(models.Model):
    """Abstract base model for tracking.

    Atribs:
        creator(obj): Creator of the object
        updater(obj): Updater of the object
        created_on(datetime): Added date of the object
        updated_on(datetime): Last updated date of the object
    """

    id = HashidAutoField(primary_key=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=None,
        null=True,
        blank=True,
        related_name="creator_%(class)s_objects",
        on_delete=models.SET_NULL,
        verbose_name=_("Creator"),
    )
    updater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        default=None,
        null=True,
        blank=True,
        related_name="updater_%(class)s_objects",
        on_delete=models.SET_NULL,
        verbose_name=_("Updater"),
    )
    updated_on = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated On")
    )
    created_on = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Updated On")
    )

    class Meta:
        """Meta class for the above model."""

        abstract = True
        ordering = ("-created_on",)

    def save(self, *args, **kwargs):
        """Override save method to add creator and updater."""
        # current_user = auth_utils.get_current_user()
        # if current_user:
        #     if not self.pk and not self.creator:
        #         self.creator = current_user
        #     self.updater = current_user
        # self.new_instance = not self.pk
        super(AbstractBaseModel, self).save(*args, **kwargs)

class AbstractAddressModel(AbstractBaseModel):
    """Abstract base model for address tracking.

    Atribs:
        address_line1(str): Address line 1
        address_line2(str): Address line 2
        city(str): City
        state(str): State
        country(str): Country
        zip_code(str): Zip code
    """

    street = models.CharField(
        max_length=255, verbose_name=_("Street"), null=True, blank=True)
    city = models.CharField(
        max_length=255, verbose_name=_("City"), null=True, blank=True)
    state = models.CharField(max_length=255, verbose_name=_("State"))
    country = models.CharField(max_length=255, verbose_name=_("Country"))
    zip_code = models.CharField(
        max_length=255, verbose_name=_("Zip Code"), null=True, blank=True)

    class Meta:
        """Meta class for the above model."""

        abstract = True