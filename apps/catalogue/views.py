# encoding: utf-8
from django.contrib import messages
from django.core.paginator import InvalidPage
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from oscar.core.loading import get_class, get_model
import json
from django.shortcuts import render_to_response
from oscar.apps.catalogue.views import ProductDetailView

ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')


def phone_selector(request):
    phones = ProductAttributeValue.objects.filter(attribute__code='kompatybilnosc').order_by('value_text'). \
        values_list('value_text', flat=True)


get_product_search_handler_class = get_class(
    'catalogue.search_handlers', 'get_product_search_handler_class')


class ProductDetailView(ProductDetailView):
    def get_context_data(self, **kwargs):
        data = super(ProductDetailView, self).get_context_data(**kwargs)
        data['description'] = self.object.title
        data['keywords'] = ' '.join([c.name for c in self.object.categories.all()])
        return data


class CatalogueOscarView(TemplateView):
    """
    Browse all products in the catalogue
    """
    context_object_name = "products"
    template_name = 'catalogue/browse.html'

    def get(self, request, *args, **kwargs):
        try:
            self.search_handler = self.get_search_handler(
                self.request.GET, request.get_full_path(), [])
        except InvalidPage:
            # Redirect to page one.
            messages.error(request, _('The given page number was invalid.'))
            return redirect('catalogue:index')
        return super(CatalogueView, self).get(request, *args, **kwargs)

    def get_search_handler(self, *args, **kwargs):
        return get_product_search_handler_class()(*args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = {}
        ctx['summary'] = _("All products")
        search_context = self.search_handler.get_search_context_data(
            self.context_object_name)
        ctx.update(search_context)
        return ctx


class CatalogueView(TemplateView):
    context_object_name = "products"
    template_name = "catalogue/browse.html"
    category = False
    prefix = ''
    filters = ['wzor', 'kolor_bazowy', 'material_glowny']
    level = 0
    product_classes = False

    def _append_category(self, c, c_list):
        if c.has_children():
            children = c.get_children() if not self.product_classes else \
                c.get_children().filter(
                    productcategory__product__product_class__external_type__in=self.product_classes.split(
                        ',')).distinct()
            for cc in children:
                c_list['nodes'].append({'text': cc.name, 'nodes': [], 'state': self._get_category_state(cc.slug, cc),
                                        'href': '/katalog/' + self.prefix +
                                                '/'.join(cc.full_slug.split('/')[self.level:])})
                self._append_category(cc, c_list['nodes'][-1])
        else:
            del c_list['nodes']
        return c_list

    def _get_category_state(self, slug, category):
        slug = slug.lower()
        path = self.request.path.lower()
        if path[-1] == '/':
            path = path[0:-1]
        path_list = path.split('/')
        state = {'expanded': False, 'selected': False}
        if path_list[-1] == slug:
            state['selected'] = True
            self.category = category
        if slug in path_list:
            state['expanded'] = True
        return state

    def get_categories(self, kwargs):
        return Category.objects.filter(depth=1)

    def get_values_grouped_by_slug(self, a):
        res = []
        vals = ProductAttributeValue.objects.filter(attribute__name=a.name).\
            order_by('value_text').values_list('id', 'value_text')
        for v in vals:
            if len(filter(lambda x: x['value_text'] == v[1], res)) == 0:
                res.append({'id': v[0], 'value_text': v[1]})
        return res

    def get_context_data(self, **kwargs):
        ctx = {'tree_data': []}
        categories = self.get_categories(kwargs)
        for c in categories:
            ctx['tree_data'].append({'text': c.name, 'nodes': [], 'state': self._get_category_state(c.slug, c),
                                     'href': '/katalog/' + self.prefix + '/'.join(c.full_slug.split('/')[self.level:])})
            ctx['tree_data'][-1] = self._append_category(c, ctx['tree_data'][-1])
        ctx['tree_data'] = json.dumps(ctx['tree_data'])
        ctx['filters'] = json.dumps(self.category.filters.split(',')) if self.category and len(
            self.category.filters) > 2 else \
            json.dumps(self.filters)
        product_attributes = ProductAttribute.objects.filter(code__in=self.filters)
        if self.category:
            categories = [c.id for c in self.category.get_descendants_and_self()]
            ctx['categories'] = '.'.join([str(c) for c in categories])
        ctx['path_list'] = []
        last_url = '/'
        path_split = [p for p in self.request.path.split('/') if p != '']
        for p in path_split[:-1]:
            ctx['path_list'].append({'name': p, 'url': last_url + p + '/'})
            last_url = ctx['path_list'][-1]['url']
        ctx['path_list'].append({'name': path_split[-1], 'url': last_url + path_split[-1] + '/'})
        ctx['product_classes'] = self.product_classes if self.product_classes else ''
        # seo
        if self.category:
            ctx['description'] = self.category.name
            ctx['keywords'] = self.category.name
        else:
            ctx['description'] = u'Katalog produktów'
            ctx['keywords'] = u'Opakowania na telefon, Obudowy na telefon, etui, folie ochronne, akcesoria telefoniczne'
        return ctx


class EtuiView(CatalogueView):
    prefix = 'opakowania-etui-folie/'
    level = 1
    product_classes = 'Opakowania,Etui,Folie'

    def get_categories(self, kwargs):
        return Category.objects.get(name='smartfony').get_children()


class CatalogueCategoryView(CatalogueView):
    def get_categories(self, kwargs):
        categories = kwargs['category_slug'].split('/')
        if len(categories) > 1:
            return Category.objects.get(slug=categories[0]).get_children()
        else:
            self.category = Category.objects.get(slug=kwargs['category_slug'])
            return self.category.get_children()


def allegro_view(request):
    product = Product.objects.get(slug=request.GET['slug'])
    return render_to_response('catalogue/allegro.html', {'product': product})
