from oscar.apps.partner.abstract_models import AbstractStockRecord


class StockRecord(AbstractStockRecord):
    def is_available(self):
        return 1 if self.num_in_stock > 0 else 0


from oscar.apps.partner.models import *
