from django import template
from oscar.apps.catalogue.models import Product


register = template.Library()


@register.inclusion_tag('templatetags/product_box.html')
def product_box(slug):
    try:
        p = {'product': Product.objects.get(slug=slug)}
    except:
        p = {}
    return p
