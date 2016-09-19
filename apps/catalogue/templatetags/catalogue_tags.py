from django import template
from apps.catalogue.models import Category
import json
from oscar.core.loading import get_model


ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')


register = template.Library()


@register.simple_tag(takes_context=True)
def render_as_template(context, template_as_string):
    template_as_string = "{% load catalogue_tags %}" + template_as_string
    template_as_object = context.template.engine.from_string(template_as_string)
    return template_as_object.render(context)


class Shop(object):

    category = False

    def __init__(self, *args, **kwargs):
        self.request = kwargs['request']
        self.category_slug = kwargs['category_slug']

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

    def get_context_data(self):
        ctx = {}
        ctx['tree_data'] = []
        categories = Category.objects.get(name=self.category_slug).get_children()
        for c in categories:
            ctx['tree_data'].append({'text': c.name, 'nodes':[], 'state': self._get_category_state(c.slug, c), 'href': c.slug})
            ctx['tree_data'][-1] = self._append_category(c, ctx['tree_data'][-1])
        ctx['tree_data'] = json.dumps(ctx['tree_data'])
        product_attributes = ProductAttribute.objects.filter(code__in=['wzor', 'kolor_bazowy', 'material_glowny'])
        if self.category:
            categories = [c.id for c in self.category.get_descendants_and_self()]
            ctx['categories'] = '.'.join([str(c) for c in categories])
            product_attributes = product_attributes.filter(product__categories__id__in=categories)
        ctx['attributes'] = {p.name: {'attributes_values': self._group_attributes(p.productattributevalue_set.all().values()),
                                      'id': p.id, 'multiselect': True if p.code in ['kolor_bazowy'] else False}
                             for p in product_attributes}
        return ctx


@register.inclusion_tag('catalogue/templatetags/shop.html', takes_context=True)
def shop(context, *args, **kwargs):
    s = Shop(request=context['request'], category_slug=kwargs.get('category', False))
    return s.get_context_data()