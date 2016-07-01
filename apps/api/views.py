from oscarapi.views import basic
from rest_framework import filters
from apps.api import serializers
import django_filters
from oscar.core.loading import get_model


Product = get_model('catalogue', 'Product')


class ProductFilter(django_filters.FilterSet):
    attribute = django_filters.CharFilter(name="attribute_values__id")
    title_like = django_filters.CharFilter(name="title", lookup_type='icontains')

    class Meta:
        model = Product
        distinct = True
        filter = ['attribute', 'title_like']
        order_by = ['title','-title']


class ProductList(basic.ProductList):
    serializer_class = serializers.ProductLinkSerializer
    filter_class = ProductFilter
    filter_backends = (filters.DjangoFilterBackend,)


    def get_queryset(self):
        return super(ProductList, self).get_queryset()