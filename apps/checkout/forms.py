from oscar.apps.address.forms import AbstractAddressForm
from oscar.core.compat import get_user_model
from oscar.core.loading import get_model
from oscar.views.generic import PhoneNumberMixin

User = get_user_model()
Country = get_model('address', 'Country')


class ShippingAddressForm(PhoneNumberMixin, AbstractAddressForm):

    def __init__(self, *args, **kwargs):
        super(ShippingAddressForm, self).__init__(*args, **kwargs)
        self.adjust_country_field()

    def adjust_country_field(self):
        countries = Country._default_manager.filter(
            is_shipping_country=True)

        # No need to show country dropdown if there is only one option
        if len(countries) == 1:
            self.fields.pop('country', None)
            self.instance.country = countries[0]
        else:
            self.fields['country'].queryset = countries
            self.fields['country'].empty_label = None

        self.fields['country'].initial = countries.get(printable_name='Poland')

    class Meta:
        model = get_model('order', 'shippingaddress')
        fields = [
            'title', 'first_name', 'last_name',
            'line1', 'line2', 'line3', 'line4',
            'postcode', 'country',
            'phone_number', 'notes',
        ]