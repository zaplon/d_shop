from django.db import models

from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractProductClass, AbstractProductAttribute, AbstractProductAttributeValue
from oscar.core.loading import get_model


class Product(AbstractProduct):
    video_url = models.URLField(blank=True, null=True)
    external_id = models.IntegerField(blank=True, null=True)

    def get_number(self):
        return self.stockrecords.first().num_in_stock

    def get_sell_details(self):
        details = {}


class ProductClass(AbstractProductClass):
    external_type = models.CharField(max_length=50, blank=True, null=True)


class ProductAttribute(AbstractProductAttribute):
    pass


class ProductAttributeValue(AbstractProductAttributeValue):
    slug = models.CharField(max_length=50, unique=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = "%s_%s" % (self.attribute.name, self.value_text)
        super(ProductAttributeValue, self).save(force_insert=False, force_update=False, using=None, update_fields=None)


from oscar.apps.catalogue.models import *
