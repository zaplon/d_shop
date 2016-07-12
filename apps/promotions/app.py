from django.conf.urls import url
from oscar.apps.promotions.app import PromotionsApplication as CorePromotionsApplication
from apps.catalogue.views import ProductClassView

class PromotionsApplication(CorePromotionsApplication):

    def get_urls(self):
        urlpatterns = super(PromotionsApplication, self).get_urls()
        # urlpatterns += [
        #     url(r'^(?P<product_classes>\w+)/(?P<attributes>\w+)/', ProductClassView.as_view(), name='product-class'),
        # ]
        return self.post_process_urls(urlpatterns)

application = PromotionsApplication()