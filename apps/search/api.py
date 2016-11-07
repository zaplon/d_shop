from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from oscar.core.loading import get_class, get_model
from apps.api.serializers import ProductElasticSerializer
from django.conf import settings
import requests

Product = get_model('catalogue', 'Product')


def update_product(id):
    p = Product.objects.get(id=id)
    data = ProductElasticSerializer(p).data
    res = requests.post('%s/%s' % (settings.ELASTIC_URL, p.external_id), data=data)
    if res.status_code == 200:
        print '%s updated successfully' % p.title
    else:
        print 'there was error updating %s' % p.title
