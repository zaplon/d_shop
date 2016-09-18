from oscarapi.views import basic
from rest_framework import filters
from apps.api import serializers
import django_filters
from oscar.core.loading import get_model
from django_filters import Filter
from django_filters.fields import Lookup
from django.shortcuts import HttpResponse
import json


class ListFilter(Filter):
    def filter(self, qs, value):
        query = super(ListFilter, self)
        for v in value.split(u","):
            values_list = v.split('.')
            if len(values_list) > 1:
                qs = query.filter(qs, Lookup(values_list, "in"))
            else:
                qs = query.filter(qs, Lookup(values_list[0], 'exact'))
        return qs


Product = get_model('catalogue', 'Product')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')


class ProductFilter(django_filters.FilterSet):
    attributes = ListFilter(name="attribute_values__value_text")
    categories = ListFilter(name="categories__id")
    title_like = django_filters.CharFilter(name="title", lookup_type='icontains')

    class Meta:
        model = Product
        distinct = True
        filter = ['attribute', 'title_like', 'categories']
        order_by = ['title', '-title']


class ProductList(basic.ProductList):
    paginate_by = 30
    serializer_class = serializers.ProductSerializer
    filter_class = ProductFilter
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        queryset = super(ProductList, self).get_queryset()
        return queryset


def get_available_attributes(request):
    atts = json.loads(request.GET['attributes'])
    res = []
    for a in atts:
        pav = ProductAttributeValue.objects.get(id=request.GET['id'])
        res.append({'id': pav.id, 'options': pav.get_available_attributes()})
    return HttpResponse(json.dumps(res), content_type='application_json')

