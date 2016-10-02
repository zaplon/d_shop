from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from oscar.core.loading import get_class, get_model
from apps.api.serializers import ProductElasticSerializer
from django.conf import settings
import requests

Product = get_model('catalogue', 'Product')


class Command(BaseCommand):
    help = "List all templates."
    args = "[appname [appname2 [...]]]"

    def handle(self, *app_labels, **options):
        for p in Product.objects.all():
            data = ProductElasticSerializer(p).data
            requests.post(settings.ELASTIC_URL, data=data)
