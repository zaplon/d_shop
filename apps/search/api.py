from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from oscar.core.loading import get_class, get_model
from rest_framework.renderers import JSONRenderer

from apps.api.serializers import ProductElasticSerializer
from django.conf import settings
import requests

Product = get_model('catalogue', 'Product')


def update_product(id):
    p = Product.objects.get(id=id)
    data = JSONRenderer().render(ProductElasticSerializer(p).data)
    res = requests.post('%s/%s' % (settings.ELASTIC_URL + 'product/', p.external_id), data=data)
    if res.status_code >= 200 and res.status_code < 300:
        print '%s updated successfully' % p.title
    else:
        print res.__dict__
        print 'there was error updating %s' % p.title
        
def update_category(c):
    data = JSONRenderer().render({'full_name': c.full_name, 'name': c.name})
    res = requests.post('%s/%s' % (settings.ELASTIC_URL + 'category/' , c.id), data=data)
    if res.status_code >= 200 and res.status_code < 300:
        print '%s updated successfully' % c.name
    else:
        print res.__dict__
        print 'there was error updating %s' % c.name

