from oscar.apps.shipping import repository, methods


class Repository(repository.Repository):

    def get_available_shipping_methods(self, basket, user=None, shipping_addr=None, request=None, **kwargs):
        return methods.Free(), methods.FixedPrice(10, 10)
