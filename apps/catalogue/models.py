from django.db import models

from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractProductClass, AbstractProductAttribute, \
    AbstractProductAttributeValue, AbstractProductCategory, AbstractCategory
from oscar.core.loading import get_model


class Category(AbstractCategory):
    filters = models.CharField(max_length=100, default='', verbose_name=u'Filtry')

    def get_ids(self):
        res = []
        for a in self.get_ancestors_and_self():
            res.append(str(a.id))
        return  ' '.join(res)


class ProductCategory(AbstractProductCategory):
    pass  # filters = models.CharField(max_length=100, default='', verbose_name=u'Filtry')


class Product(AbstractProduct):
    video_url = models.URLField(blank=True, null=True)
    external_id = models.IntegerField(blank=True, null=True)

    def get_number(self):
        return self.stockrecords.first().num_in_stock

    def get_sell_details(self):
        details = {}

    def get_query_suggestions(self):
        atts = [v.value for v in self.attribute_values.all()]
        inputs = [self.product_class.name] + atts + [self.title]
        return {'input': inputs}


class ProductClass(AbstractProductClass):
    external_type = models.CharField(max_length=50, blank=True, null=True)


class ProductAttribute(AbstractProductAttribute):
    pass


class ProductAttributeValue(AbstractProductAttributeValue):
    slug = models.CharField(max_length=50, unique=False)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.slug = "%s_%s" % (self.attribute.name, self.value_text)
        super(ProductAttributeValue, self).save(force_insert=False, force_update=False, using=None, update_fields=None)


from oscar.apps.catalogue.models import *
