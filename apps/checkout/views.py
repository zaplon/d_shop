from oscar.apps.checkout.views import PaymentDetailsView
from oscar.apps.payment import models


class PaymentDetailsView(PaymentDetailsView):
    def render_preview(self, request, **kwargs):
        """
        Show a preview of the order.
        If sensitive data was submitted on the payment details page, you will
        need to pass it back to the view here so it can be stored in hidden
        form inputs.  This avoids ever writing the sensitive data to disk.
        """
        self.preview = True
        ctx = self.get_context_data(**kwargs)
        ctx['payment_method'] = request.POST['payment-method']
        return self.render_to_response(ctx)
    
    def handle_payment(self, order_number, total, **kwargs):
        # Talk to payment gateway.  If unsuccessful/error, raise a
        # PaymentError exception which we allow to percolate up to be caught
        # and handled by the core PaymentDetailsView.
        #reference = gateway.pre_auth(order_number, total.incl_tax, kwargs['bankcard'])

        # Payment successful! Record payment source
        source_type, __ = models.SourceType.objects.get_or_create(
            name=u"Płatność przy odbiorze")
        source = models.Source(
            source_type=source_type,
            amount_allocated=total.incl_tax)
        self.add_payment_source(source)

        # Record payment event
        self.add_payment_event('pre-auth', total.incl_tax)
