# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import untangle
from apps.catalogue.models import ProductClass, Product, ProductImage
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.core.loading import get_model
from django.core.exceptions import ObjectDoesNotExist
import wget
from django.conf import settings
import os
import datetime
import shutil


Category = get_model('catalogue', 'category')
StockRecord = get_model('partner', 'stockrecord')
Partner = get_model('partner', 'partner')
ProductCategory = get_model('catalogue', 'productcategory')
ProductAttribute = get_model('catalogue', 'productattribute')
ProductAttributeValue = get_model('catalogue', 'productattributevalue')

OSCAR_IMAGES_FOLDER = datetime.datetime.now().strftime(settings.OSCAR_IMAGE_FOLDER)
DOWNLOAD_FOLDER = os.path.join(settings.BASE_DIR, 'public', 'media', OSCAR_IMAGES_FOLDER)

FRONT_URL_ROOT = OSCAR_IMAGES_FOLDER


class Command(BaseCommand):
    help = 'Import data for catalogue'
    fields_map = {'title': 'nazwa', 'external_id': 'ProduktId', 'description': 'opis'}
    breadcrumbs = []
    partner = Partner.objects.get(code='forcetop')
    escape_map = {'ą': 'a', 'ę': 'e', 'ł': 'l', 'ś': 's', 'ć': 'c', 'ó': 'o', 'ż': 'z', 'ź': 'z', '/':'_', '\\': '_'}

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--get-images',
                            action='store_true',
                            dest='get_images',
                            help='Get product images')

        parser.add_argument('--delete-all',
                            action='store_true',
                            dest='delete_all',
                            help='Delete all before import')

    def slugify(self, text):
        text = text.replace(' ', '_').lower().encode('utf-8')
        for e in self.escape_map:
            text = text.replace(e, self.escape_map[e])
        return text

    def add_prices(self, p, node):
        try:
            sr = StockRecord.objects.get(product=p, partner=self.partner)
        except:
            sr = StockRecord(product=p, partner=self.partner)
        sr.partner_sku = node.kod.cdata
        sr.price_excl_tax = node.cenasrp_netto.cdata.replace(',', '.')
        sr.price_retail = node.cenasrp_brutto.cdata.replace(',', '.')
        sr.cost_price = node.cena_brutto.cdata.replace(',', '.')
        sr.num_in_stock = int(0 if node.stan.cdata < 5 else float(node.stan.cdata) - 5)
        sr.low_stock_threshold = 5
        sr.save()

    def add_images(self, p, node):
        for i, zdjecie in enumerate(node.zdjecie):
            caption = self.slugify(p.title + ' ' + str(i))
            try:
                if i > 0:
                    file_name = wget.download(zdjecie.cdata, out=self.slugify(p.title + '_' + str(i) + '.jpg'))
                else:
                    file_name = wget.download(zdjecie.cdata, out=self.slugify(p.title + '.jpg'))
                front = os.path.join(FRONT_URL_ROOT, file_name)
                ProductImage.objects.create(product=p, original=front, caption=caption, display_order=i)
                move_from = os.path.join(file_name)
                move_to = os.path.join(DOWNLOAD_FOLDER, file_name)
                shutil.move(move_from, move_to)
                print file_name
            except:
                print 'No image  for product %s (%s)' % (p.title, i)

    def handle(self, *args, **options):
        #tworzenie katalogu
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)
        # importowane klasy produktów
        klasses = ProductClass.objects.filter(external_type__isnull=False)
        e_types = {k.external_type: k for k in klasses}
        get_images = options.get('get_images', False)
        delete_all = options.get('delete_all', False)
        # delete_all = True
        # get_images = True
        if delete_all:
            Product.objects.all().delete()
            ProductAttribute.objects.all().delete()
            Category.objects.all().delete()
            StockRecord.objects.all().delete()
        xml_file = wget.download('http://www.b2btrade.pl/pobierzOferte.aspx?user=GEEKMAN', out='catalogue.xml')

        # poprawka pliku
        buffor_file = file(xml_file)
        buffor = buffor_file.read()
        buffor = buffor[41:]
        buffor_file.close()
        buffor_file = file('_tmp.xml', mode='w')
        buffor_file.write(buffor)
        buffor_file.close()
        obj = untangle.parse('_tmp.xml')

        counter = 0
        for p in obj.produkty.produkt:
            if counter > 200:
                break
            counter += 1
            p_type = ''
            if getattr(p, 'atrybuty', False):
                for a in p.atrybuty.atrybut:
                    if a['name'] == 'Typ':
                        p_type = a.cdata
            if p_type not in e_types:
                continue
            try:
                p_obj = Product.objects.get(external_id=p.ProduktId.cdata)
            except ObjectDoesNotExist:
                p_obj = Product(product_class=e_types[p_type])
            for f in self.fields_map:
                setattr(p_obj, f, getattr(p, self.fields_map[f]).cdata)
            p_obj.save()
            print p_obj.title

            for k in p.kategorie.kategoria:
                path = k.cdata
                breadcrumb_list = path.split('/')
                breadcrumb = ' > '.join(breadcrumb_list)
                filtered_b = filter(lambda x: x['path'] == breadcrumb, self.breadcrumbs)
                if len(filtered_b) == 0:
                    self.breadcrumbs.append({'path': breadcrumb, 'products': [], 'external_id': k['id']})
                    b = self.breadcrumbs[-1]
                else:
                    b = filtered_b[0]
                b['products'].append(p.ProduktId.cdata)

            for a in p.atrybuty.atrybut:
                if not a['name'] == 'Typ':
                    try:
                        pa = ProductAttribute.objects.get(product_class=p_obj.product_class, code=self.slugify(a['name']))
                    except ObjectDoesNotExist:
                        pa = ProductAttribute.objects.create(product_class=p_obj.product_class,
                                                             code=self.slugify(a['name']), type='text')
                    pa.name = a['name']
                    pa.save()
                    try:
                        pav = ProductAttributeValue.objects.get(product=p_obj, attribute=pa)
                    except ObjectDoesNotExist:
                        pav = ProductAttributeValue.objects.create(product=p_obj, attribute=pa)
                    pav.value = a.cdata
                    pav.save()
            self.stdout.write('Product %s saved' % p_obj.title)
            if get_images:
                self.add_images(p_obj, p.zdjecia)
            self.add_prices(p_obj, p)
        print self.breadcrumbs
        for b in self.breadcrumbs:
            obj = create_from_breadcrumbs(b['path'])
            for p in b['products']:
                p = Product.objects.get(external_id=p)
                ProductCategory.objects.get_or_create(product=p, category=obj)
        self.stdout.write('Successfully imported data')
