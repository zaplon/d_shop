# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import untangle
from apps.catalogue.models import ProductClass, Product, ProductImage
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.core.loading import get_model
import wget
import os


Category = get_model('catalogue', 'category')
StockRecord = get_model('partner', 'stockrecord')
Partner = get_model('partner', 'partner')
ProductCategory = get_model('catalogue', 'productcategory')


class Command(BaseCommand):
    help = 'Import data for catalogue'
    fields_map = {'title': 'nazwa', 'external_id': 'ProduktId', 'description': 'opis'}
    categories = {}
    breadcrumbs = []
    partner = Partner.objects.get(code='forcetop')

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

        parser.add_argument('--delete-all',
                            action='store_true',
                            dest='delete-all',
                            help='Delete all before import')


    def add_prices(self, p, node):
        try:
            sr = StockRecord.objects.get(product=p, partner=self.partner)
        except:
            sr = StockRecord(product=p, partner=self.partner)
        sr.price_excl_tax = node.cenasrp_netto.cdata
        sr.price_retail = node.cenasrp_brutto.cdata
        sr.cost_price = node.cena_brutto.cdata
        sr.num_in_stock = 0 if node.stan.cdata < 5 else node.stan.cdata - 5
        sr.low_stock_threshold = 5
        sr.save()
        
    def add_images(self, p, node):
        for i, zdjecie in enumerate(node.zdjecie):
            caption = p.title + ' ' + str(i)
            #out = os.path.join(os.getcwd(), 'public', 'media', 'images', 'products', caption + '.jpg')
            out = caption + '.jpg'
            file_name = wget.download(zdjecie.cdata, out=out)
            ProductImage.objects.create(product=p, original=file_name, caption=caption, display_order=i)
            os.remove(file_name)

    def handle(self, *args, **options):
        # importowane klasy produktów
        klasses = ProductClass.objects.filter(external_type__isnull=False)
        e_types = {k.external_type: k for k in klasses}
        file = options.get('file')
        get_images = options.get('get_images', False)
        delete_all = options.get('delete-all', False)
        delete_all = get_images = True
        if delete_all:
            Product.objects.all().delete()
            Category.objects.all().delete()
            StockRecord.objects.all().delete()
        obj = untangle.parse(file)
        for p in obj.xml.produkty.produkt:
            k_ids = []
            for k in p.kategorie.kategoria:
                path = k.cdata
                breadcrumb_list = path.split('/')
                breadcrumb = ' > '.join(breadcrumb_list)
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
                self.categories[breadcrumb_list[-1]] = []
            self.categories[breadcrumb_list[-1]].append(p.ProduktId)
            try:
                p_obj = Product.objects.get(external_id=p.ProduktId.cdata)
            except:
                p_obj = Product(product_class=e_types[p_type])
            for f in self.fields_map:
                setattr(p_obj, f, getattr(p, self.fields_map[f]).cdata)
            p_obj.save()
            self.stdout.write('Product %s saved' % p_obj.title)
            if get_images:
                self.add_images(p_obj, p.zdjecia)
        print self.categories
        for b in self.breadcrumbs:
            create_from_breadcrumbs(b)
        for category in self.categories:
            for c in self.categories[category]:
                print category
                obj = Category.objects.get(name=category)
                p = Product.objects.get(external_id=c.cdata)
                ProductCategory.objects.get_or_create(product=p, category=obj)
        self.stdout.write('Successfully imported data')
