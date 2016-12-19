# encoding: utf-8
from crispy_forms.layout import Layout
from django.forms import Form
from django.forms.fields import CharField, EmailField
from django.forms import Textarea
from crispy_forms.helper import FormHelper
from django.core.mail import send_mail


class ShopForm(Form):

    def submit_form(self):
        res = send_mail(self.get_topic(), self.to_html(), self.get_sender(), ['kontakt@obudowynatelefon.pl'],fail_silently=False)
        return res


class ContactForm(ShopForm):
    name = CharField(max_length=150, label=u"Imię")
    email = EmailField(label=u'Adres email')
    question = CharField(max_length=500, label=u'Pytanie', widget=Textarea)
    phone = CharField(max_length=20, required=False, label=u'Numer telefonu')

    def get_topic(self):
        return 'Formularz kontaktowy'

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'name',
            'email',
            'phone',
            'question'
        )
