from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class OfferConfig(AppConfig):
    label = 'offer'
    name = 'apps.offer'
    verbose_name = _('Offer')
