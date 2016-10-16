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
from django.db.models import Min, Max
from django.db.models import Case, When, BooleanField


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
        if request.GET.get('start', False) and request.GET.get('end', False):
            queryset = queryset.filter(stockrecords__price_retail__gte=float(request.GET.get('start')),
                                       stockrecords__price_retail__lte=float(request.GET.get('end')))
        if not request.GET.get('dont_refresh_filters', False):
            filters = get_available_attributes(request, queryset)
        else:
            filters = None

        queryset = queryset.annotate(in_stock=Case(When(stockrecords__num_in_stock__gt=1, then=True), default=False,
                                                   output_field=BooleanField()), price=Min('stockrecords__price_retail'))

        if 'order' in request.GET:
            order = request.GET['order'].replace('-', '')
            if order == 'price':
                order = 'price'
            if request.GET['order'][0] == '-':
                order = '-' + order
            if 'name' in order:
                ordering = [order, 'name']
            else:
                ordering = [order]
            ordering = ['-in_stock'] + ordering
            queryset = queryset.order_by(*ordering)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({'products': serializer.data, 'filters': filters, 
                                                'prices': get_price_range(request, queryset)})

        serializer = self.get_serializer(queryset, many=True)
        return Response({'products': serializer.data, 'filters': filters, 
                         'prices': get_price_range(request, queryset)})

    def get_queryset(self):
        queryset = super(ProductList, self).get_queryset()
        return queryset


def get_price_range(request, products):
    min_val = products.aggregate(Min('stockrecords__price_retail'))['stockrecords__price_retail__min']
    max_val = products.aggregate(Max('stockrecords__price_retail'))['stockrecords__price_retail__max']
    start = request.GET['start'] if request.GET.get('start', False) else min_val
    end = request.GET['end'] if request.GET.get('end', False) else max_val
    if start < min_val:
        start = min_val
    if end > max_val:
        end = max_val
    return {'min': min_val, 'max': max_val, 'range': {'start': float(start), 'end': float(end)}}


def get_available_attributes(request, products):
    filters = json.loads(request.GET['filters'])
    res = []
    for f in filters:
        pavs = ProductAttributeValue.objects.filter(product__in=products, attribute__code=f).order_by('value_text', 'id')
        options = [{'id': int(pav.id), 'text': pav.value_text, 'slug': pav.value_text} for pav in pavs]
        if len(options) > 0:
            options_unique = [options[0]]
            name = pavs[0].attribute.name
            for i in range(1, len(options)):
                if options[i-1]['text'] != options[i]['text']:
                    options_unique.append(options[i])
        else:
            options_unique = []
            name = None
        res.append({'name': name, 'options': options_unique, 'slug': f})
    return res
