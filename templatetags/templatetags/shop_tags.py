from django import template
from apps.catalogue.models import Product, Category


register = template.Library()


@register.inclusion_tag('templatetags/product_box.html')
def product_box(slug):
    try:
        p = {'product': Product.objects.get(slug=slug)}
    except:
        p = {'product': Product.objects.all()[0]}
    return p


@register.inclusion_tag('templatetags/box.html')
def category_box(slug):
    c = Category.objects.get(slug=slug)
    image = getattr(c, 'image', None)
    return {'title': c.name, 'url': c.get_absolute_url(), 'image': c.image.url if c.image else None}

