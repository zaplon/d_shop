from oscarapi.views import basic
from rest_framework import filters
from apps.api import serializers
import django_filters
from oscar.core.loading import get_model
from django_filters import Filter
from django_filters.fields import Lookup


class ListFilter(Filter):
    def filter(self, qs, value):
        return super(ListFilter, self).filter(qs, Lookup(value.split(u","), "in"))


Product = get_model('catalogue', 'Product')


class ProductFilter(django_filters.FilterSet):
    attributes = ListFilter(name="attribute_values__id")
    title_like = django_filters.CharFilter(name="title", lookup_type='icontains')

    class Meta:
        model = Product
        distinct = True
        filter = ['attribute', 'title_like']
        order_by = ['title', '-title']


class ProductList(basic.ProductList):
    paginate_by = 30
    serializer_class = serializers.ProductSerializer
    filter_class = ProductFilter
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        queryset = super(ProductList, self).get_queryset()
        return queryset
