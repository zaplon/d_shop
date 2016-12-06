from oscar.apps.partner.abstract_models import AbstractStockRecord


class StockRecord(AbstractStockRecord):
    def is_available(self):
        return self.num_in_stock > 0


from oscar.apps.partner.models import *
