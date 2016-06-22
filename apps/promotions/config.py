from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PromotionsConfig(AppConfig):
    label = 'shop.promotions'
    name = 'apps.promotions'
    verbose_name = _('Promotions')
