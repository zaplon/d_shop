from django.contrib import messages
from django.core.paginator import InvalidPage
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from oscar.apps.catalogue.models import ProductAttributeValue, ProductAttribute
from oscar.core.loading import get_class, get_model
import json
from oscar.apps.catalogue.models import Category


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
    filters = ['wzor', 'kolor_bazowy', 'material_glowny']

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
                                        'href': '/catalogue/etui/' + '/'.join(cc.full_slug.split('/')[1:])})
                self._append_category(cc, c_list['nodes'][-1])
        return c_list

    def _get_category_state(self, name, category):
        name = name.lower()
        path_list = self.request.path.lower().split('/')
        state = {'expanded': False, 'selected': False}
        if path_list[-1] == name:
            state['selected'] = True
            self.category = category
        if name in path_list:
            state['expanded'] = True
        return state

    def get_categories():
        return Category.objects.get(name='smartfony').get_children()

    def get_context_data(self, **kwargs):
        ctx = {}
        ctx['tree_data'] = []
        categories = self.get_categories()
        for c in categories:
            ctx['tree_data'].append({'text': c.name, 'nodes':[], 'state': self._get_category_state(c.slug, c), 'href': c.slug})
            ctx['tree_data'][-1] = self._append_category(c, ctx['tree_data'][-1])
        #ctx['tree_data'] = [{'text': 'Apple', 'nodes': [{'text': 'Iphone'}]}]
        ctx['tree_data'] = json.dumps(ctx['tree_data'])
        product_attributes = ProductAttribute.objects.filter(code__in=self.filters)
        if self.category:
            categories = [c.id for c in self.category.get_descendants_and_self()]
            ctx['categories'] = '.'.join([str(c) for c in categories])
            product_attributes = product_attributes.filter(product__categories__id__in=categories)
        ctx['attributes'] = {p.name: {'attributes_values': self._group_attributes(p.productattributevalue_set.all().values()),
                                      'id': p.id, 'multiselect': True if p.code in ['kolor_bazowy'] else False}
                             for p in product_attributes}
        return ctx


class ProductClassView(TemplateView):
    context_object_name = "products"
    template_name = "catalogue/etui.html"

    def get_context_data(self, **kwargs):
        ctx = {}
        ctx['attributes'] = {p.name: {'values': p.productattributevalue_set.all().values(), 'id': p.id,
                                      'multiselect': True if p.code in ['kolor_bazowy'] else False}
                             for p in ProductAttribute.objects.filter(code__in=['wzor', 'kompatybilnosc',
                                                                                'kolor_bazowy'])}
        return ctx
