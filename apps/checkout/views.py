from oscar.apps.checkout.views import PaymentDetailsView


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