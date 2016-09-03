# -*- coding: utf-8 -*-s
from oscar.apps.shipping import repository, methods
from decimal import *


class FixedPrice(methods.FixedPrice):
    name = u'Przesyłka kurierska'


class Repository(repository.Repository):

    def get_available_shipping_methods(self, basket, user=None, shipping_addr=None, request=None, **kwargs):
        if basket.total_incl_tax > 100:
            return [methods.Free()]
        else:
            return [FixedPrice(Decimal(10.0), Decimal(10.0))]
