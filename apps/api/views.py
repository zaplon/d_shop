from oscarapi.views import basic
from rest_framework import filters
from apps.api import serializers
import django_filters
from oscar.core.loading import get_model
from django_filters import Filter
from django_filters.fields import Lookup
from django.shortcuts import HttpResponse
import json
from rest_framework.response import Response


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
ProductAttribute = get_model('catalogue', 'ProductAttribute')
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        filters = get_available_attributes(request, queryset)
        return Response({'products': serializer.data, 'filters': filters})

    def get_queryset(self):
        queryset = super(ProductList, self).get_queryset()
        return queryset


def get_available_attributes(request, products):
    filters = json.loads(request.GET['filters'])
    res = []
    for f in filters:
        pavs = ProductAttributeValue.objects.filter(product__in=products, attribute__name=f)
        options = [{'id': int(pav.id), 'text': pav.value_text} for pav in pavs]
        res.append({'name': f, 'options': options})
    return res
