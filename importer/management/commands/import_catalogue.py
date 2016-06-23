# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import untangle
from apps.catalogue import ProductClass, Product
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.core.loading import get_model


Category = get_model('catalogue', 'category')


class Command(BaseCommand):
    help = 'Import data for catalogue'
    fields_map = {'name': 'nazwa', 'external_id': 'ProduktId'}
    categories = {}
    breadcrumbs = {}
    def add_arguments(self, parser):
         # Named (optional) arguments
        parser.add_argument('--file',
            action='store_true',
            dest='file',
            default='catalogue.xml',
            help='Name of the XML file to import')

    def handle(self, *args, **options):
            #importowane klasy produktów
            e_ids = ProductClass.objects.filter(external_id__isnull=False).values_list('external_id', flat=True)
            file = options.get('file')
            obj = untangle.parse(file)
            for p in obj.xml.produkty.produkt:
                k_ids = []
                for k in p.kategorie.kategoria:
                    path = k.cdata
                    breadcrumb = path.split('/')
                    breadcrumb = ' > '.join(breadcrumb)
                    k_ids.append(k['id'])
                if len(set(k_ids) & set(e_ids)) == 0:
                    continue
                if not breadcrumb in self.breadcrumbs:
                    self.breadcrumbs.append(breadcrumb)
                if not breadcrumb[-1] in self.categories:
                        self.categories[breadcrumb[-1]] = []
                self.categories[breadcrumb[-1]].append(p.ProduktId)
                try:
                    p = Product.objects.get(id=p.ProduktId)
                except:
                    p = Product()
                for f in self.fields_map:
                    setattr(p, f, fields_map[f])
                p.save()
            create_from_breadcrumbs(breadcrumbs)
            for category in self.categories:
                for c in self.categories[category]:
                    obj = Category.objects.get(name=category)
                    p = Product.objects.get(external_id=c)
                    p.categories.add(obj)
            self.stdout.write('Successfully imported data')
