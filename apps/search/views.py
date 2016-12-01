from django.http import HttpResponse
from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.api.serializers import ProductElasticSerializer
from oscar.core.loading import get_model
#from elasticsearch import Elasticsearch
#es = Elasticsearch()
import requests
from django.conf import settings


Product = get_model('catalogue', 'Product')


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductElasticSerializer


def rest_view(request):
    if request.method == 'POST':
        res = requests.post(settings.ELASTIC_URL + '_search/', data=request.body)
        #res = es.search(index="shop", body=request.POST.body)
        return HttpResponse(res.content, content_type='application/json')

