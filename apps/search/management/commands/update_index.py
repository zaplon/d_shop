from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from oscar.core.loading import get_class, get_model
from apps.search.api import update_product

Product = get_model('catalogue', 'Product')


class Command(BaseCommand):
    help = "Refresh index"
    args = ""

    def handle(self, *app_labels, **options):
        for p in Product.objects.all()[:200]:
            update_product(p.id)
