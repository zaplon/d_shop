# encoding: utf-8
from django.contrib import messages
from django.core.paginator import InvalidPage
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from oscar.core.loading import get_class, get_model
import json
from oscar.apps.catalogue.models import Category
from django.shortcuts import render_to_response


ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
Product = get_model('catalogue', 'Product')


def phone_selector(request):
    phones = ProductAttributeValue.objects.filter(attribute__code='kompatybilnosc').order_by('value_text').\
        values_list('value_text', flat=True)


get_product_search_handler_class = get_class(
    'catalogue.search_handlers', 'get_product_search_handler_class')


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

    @staticmethod
    def _group_attributes(atts):
        new_atts = {}
        for a in atts:
            if a['value_text'] not in new_atts:
                new_atts[a['value_text']] = {'ids': []}
            new_atts[a['value_text']]['ids'].append(str(a['id']))
        for a in new_atts:
            new_atts[a]['ids'] = ','.join(new_atts[a]['ids'])
        return new_atts

    def _append_category(self, c, c_list):
        if c.has_children():
            for cc in c.get_children():
                c_list['nodes'].append({'text': cc.name, 'nodes': [], 'state': self._get_category_state(cc.slug, cc),
                                        'href': '/katalog/' + self.prefix +
                                                '/'.join(cc.full_slug.split('/')[self.level:])})
                self._append_category(cc, c_list['nodes'][-1])
        else:
            del c_list['nodes']
        return c_list

    def _get_category_state(self, name, category):
        name = name.lower()
        path = self.request.path.lower()
        if path[-1] == '/':
            path = path[0:-1]
        path_list = path.split('/')
        state = {'expanded': False, 'selected': False}
        if path_list[-1] == name:
            state['selected'] = True
            self.category = category
        if name in path_list:
            state['expanded'] = True
        return state

    def get_categories(self, kwargs):
        #return Category.objects.get(name='smartfony').get_children()
        return Category.objects.filter(depth=1)

    def get_values_grouped_by_slug(self, a):
        res = []
        vals = ProductAttributeValue.objects.filter(attribute__name=a.name).order_by('value_text').values_list('id', 'value_text')
        for v in vals:
            if len(filter(lambda x: x['value_text'] == v[1], res)) == 0:
                res.append({'id': v[0], 'value_text': v[1]})
        return res

    def get_context_data(self, **kwargs):
        ctx = {'filters': json.dumps(self.filters), 'tree_data': []}
        categories = self.get_categories(kwargs)
        for c in categories:
            ctx['tree_data'].append({'text': c.name, 'nodes':[], 'state': self._get_category_state(c.slug, c),
                                     'href': c.slug})
            ctx['tree_data'][-1] = self._append_category(c, ctx['tree_data'][-1])
        ctx['tree_data'] = json.dumps(ctx['tree_data'])
        product_attributes = ProductAttribute.objects.filter(code__in=self.filters)
        if self.category:
            categories = [c.id for c in self.category.get_descendants_and_self()]
            ctx['categories'] = '.'.join([str(c) for c in categories])
        #     product_attributes = product_attributes.filter(product__categories__id__in=categories)
        # ctx['attributes'] = {p.name: {'attribute_values': self.get_values_grouped_by_slug(p.name),  # self._group_attributes(p.productattributevalue_set.all().values()),
        #                               'name': p.name, 'multiselect': True if p.code in ['kolor_bazowy'] else False}
        #                      for p in product_attributes}
        ctx['path_list'] = []
        last_url = '/'
        path_split = [p for p in self.request.path.split('/') if p != '']
        for p in path_split[:-1]:
            ctx['path_list'].append({'name': p, 'url': last_url + p + '/'})
            last_url = ctx['path_list'][-1]['url']
        ctx['path_list'].append({'name': path_split[-1], 'url': last_url + path_split[-1] + '/'})
        return ctx


class EtuiView(CatalogueView):
    prefix = 'opakowania-etui-folie/'
    level = 1

    def get_categories(self, kwargs):
        return Category.objects.get(name='smartfony').get_children()


class CatalogueCategoryView(CatalogueView):

    def get_categories(self, kwargs):
        categories = kwargs['category_slug'].split('/')
        if len(categories) > 1:
            return Category.objects.get(slug=categories[0]).get_children()
        else:
            return Category.objects.get(slug=kwargs['category_slug']).get_children()


def allegro_view(request):
    product = Product.objects.get(id=request.GET['id'])
    return render_to_response('catalogue/allegro.html', {'product': product})
