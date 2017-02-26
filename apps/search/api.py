from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from oscar.core.loading import get_class, get_model
from rest_framework.renderers import JSONRenderer

from apps.api.serializers import ProductElasticSerializer
from django.conf import settings
import requests
from PIL import Image
import os

Product = get_model('catalogue', 'Product')


def make_thumbnail(img):
    img_name = img.split('/')[-1]
    thumbnail_target = os.path.join(settings.MEDIA_ROOT, 'images', 'thumbnail', img_name)
    thumbnail_link = settings.MEDIA_URL + '/images/thumbnail/' + img_name
    if os.path.isfile(thumbnail_target):
        return thumbnail_link
    basewidth = 300
    try:
        i = Image.open(settings.BASE_DIR + '/public' + img)
    except:
        return img
    if i.size[0] <= 300:
        return img
    wpercent = (basewidth/float(i.size[0]))
    hsize = int((float(i.size[1])*float(wpercent)))
    i = i.resize((basewidth,hsize), Image.ANTIALIAS)
    i.save(thumbnail_target)
    return thumbnail_link


def update_product(id):
    p = Product.objects.get(id=id)
    d = ProductElasticSerializer(p).data
    if len(d['images']) > 0:
        d['images'][0]['original'] = make_thumbnail(d['images'][0]['original'])
    data = JSONRenderer().render(d)
    res = requests.post('%s%s' % (settings.ELASTIC_URL + 'product/', p.external_id), data=data)
    if res.status_code >= 200 and res.status_code < 300:
        print '%s updated successfully' % p.title
    else:
        print res.__dict__
        print 'there was error updating %s' % p.title


def update_category(c):
    data = JSONRenderer().render({'full_name': c.full_name, 'name': c.name})
    res = requests.post('%s%s' % (settings.ELASTIC_URL + 'category/' , c.id), data=data)
    if res.status_code >= 200 and res.status_code < 300:
        print '%s updated successfully' % c.name
    else:
        print res.__dict__
        print 'there was error updating %s' % c.name

