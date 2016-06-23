# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import untangle
from apps.catalogue.models import ProductClass, Product, ProductImage
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.core.loading import get_model
import wget
import os

Category = get_model('catalogue', 'category')


class Command(BaseCommand):
    help = 'Import data for catalogue'
    fields_map = {'title': 'nazwa', 'external_id': 'ProduktId', 'description': 'opis'}
    categories = {}
    breadcrumbs = []

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--file',
                            action='store_true',
                            dest='file',
                            default='catalogue.xml',
                            help='Name of the XML file to import')
        parser.add_argument('--get-images',
                            action='store_true',
                            dest='get_images',
                            help='Get product images')

    def add_images(self, p, node):
        for zdjecie in node.zdjecie:
            file_name = wget.download(zdjecie.cdata)
            caption = p.title + file_name.split('.')[0]
            ProductImage.objects.create(product=p, image=file_name, caption=caption)
            os.remove(file_name)

    def handle(self, *args, **options):
        # importowane klasy produktów
        klasses = ProductClass.objects.filter(external_type__isnull=False)
        e_types = {k.external_type: k for k in klasses}
        file = options.get('file')
        get_images = options.get('get_images', False)
        obj = untangle.parse(file)
        for p in obj.xml.produkty.produkt:
            k_ids = []
            for k in p.kategorie.kategoria:
                path = k.cdata
                breadcrumb = path.split('/')
                breadcrumb = ' > '.join(breadcrumb)
                k_ids.append(k['id'])
            p_type = ''
            for a in p.atrybuty.atrybut:
                if a['name'] == 'Typ':
                    p_type = a.cdata
            if p_type not in e_types:
                continue
            if not breadcrumb in self.breadcrumbs:
                self.breadcrumbs.append(breadcrumb)
            if not breadcrumb[-1] in self.categories:
                self.categories[breadcrumb[-1]] = []
            self.categories[breadcrumb[-1]].append(p.ProduktId)
            try:
                p_obj = Product.objects.get(external_id=p.ProduktId)
            except:
                p_obj = Product(product_class=e_types[p_type])
            for f in self.fields_map:
                setattr(p_obj, f, getattr(p, self.fields_map[f]).cdata)
            p_obj.save()
            self.stdout.write('Product %s saved' % p_obj.title)
            if get_images:
                self.add_images(p_obj, p.zdjecia)
        for b in self.breadcrumbs:
            create_from_breadcrumbs(b)
        for category in self.categories:
            for c in self.categories[category]:
                obj = Category.objects.get(name=category)
                p = Product.objects.get(external_id=c)
                p.categories.add(obj)
        self.stdout.write('Successfully imported data')
