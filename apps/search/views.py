from django.http import HttpResponse
from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.api.serializers import ProductElasticSerializer
from oscar.core.loading import get_model
from django.views.decorators.csrf import csrf_exempt
#from elasticsearch import Elasticsearch
#es = Elasticsearch()
import requests
import json
from django.conf import settings


Product = get_model('catalogue', 'Product')


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductElasticSerializer


@csrf_exempt
def rest_view(request):
    if request.method == 'GET':
        if request.GET.get('term', False):
            data = {'completion': {'text': request.GET['term'], 'completion': {'field': 'query_suggest'}}}
            res = requests.post(settings.ELASTIC_URL + '_suggest/', data=json.dumps(data))
            res = json.loads(res.content)
            return HttpResponse(json.dumps(res['completion'][0]['options']), content_type='application/json')

    if request.method == 'POST':
        res = requests.post(settings.ELASTIC_URL + '_search/', data=request.body)
        #res = es.search(index="shop", body=request.POST.body)
        return HttpResponse(res.content, content_type='application/json')

