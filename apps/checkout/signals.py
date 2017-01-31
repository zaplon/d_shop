
from django.dispatch import receiver

from oscar.core.loading import get_class

from . import history

post_checkout = get_class('catalogue.signals', 'post_checkout')


@receiver(post_checkout)
def send_admin_email(order, user, request, response, **kwargs):
    """
    Send notification about purchase
    """
    return history.update(product, request, response)
