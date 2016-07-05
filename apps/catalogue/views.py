from django.contrib import messages
from django.core.paginator import InvalidPage
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from oscar.apps.catalogue.models import ProductAttributeValue, ProductAttribute
from oscar.core.loading import get_class, get_model


def phone_selector(request):
    phones = ProductAttributeValue.objects.filter(attribute__code='kompatybilnosc').order_by('value_text').\
        values_list('value_text', flat=True)


get_product_search_handler_class = get_class(
    'catalogue.search_handlers', 'get_product_search_handler_class')


class CatalogueView(TemplateView):
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


class EtuiView(TemplateView):

    context_object_name = "products"
    template_name = "catalogue/etui.html"

    def get_context_data(self, **kwargs):
        ctx = {}
        ctx['attributes'] = {p.name: {'values': p.productattributevalue_set.all().values(), 'id': p.id,
                                      'multiselect': True if p.code in ['kolor_bazowy'] else False}
                             for p in ProductAttribute.objects.filter(code__in=['wzor', 'kompatybilnosc',
                                                                                'kolor_bazowy'])}
        return ctx