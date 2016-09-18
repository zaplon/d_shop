from django.db import models

from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractProductClass, AbstractProductAttribute
from oscar.core.loading import get_model


ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')


class Product(AbstractProduct):
    video_url = models.URLField(blank=True, null=True)
    external_id = models.IntegerField(blank=True, null=True)


class ProductClass(AbstractProductClass):
    external_type = models.CharField(max_length=50, blank=True, null=True)


class ProductAttribute(AbstractProductAttribute):
    def get_available_values(products):
        ids = ProductAttributeValue.objects.filter(product__id__in=products, attribute=self).values_list('id', flat=True)
        return ids
    

from oscar.apps.catalogue.models import *
