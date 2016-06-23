from django.db import models

from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractProductClass


class Product(AbstractProduct):
    video_url = models.URLField(blank=True, null=True)
    external_id = models.IntegerField(blank=True, null=True)


class ProductClass(AbstractProductClass):
    external_type = models.CharField(max_length=50, blank=True, null=True)


from oscar.apps.catalogue.models import *
