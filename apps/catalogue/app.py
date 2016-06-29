from django.conf.urls import url
from oscar.apps.catalogue.app import CatalogueApplication as CorePromotionsApplication
from .views import EtuiView

class CatalogueApplication(CorePromotionsApplication):
    etui_view = EtuiView

    def get_urls(self):
        urlpatterns = super(CatalogueApplication, self).get_urls()
        urlpatterns += [
            url(r'^etui/', self.catalogue_view.as_view(), name='index'),
            url(r'^$', self.etui_view.as_view(), name='etui'),
            url(r'^(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                self.detail_view.as_view(), name='detail'),
            url(r'^kategoria/(?P<category_slug>[\w-]+(/[\w-]+)*)_(?P<pk>\d+)/$',
                self.category_view.as_view(), name='category'),
            # Fallback URL if a user chops of the last part of the URL
            url(r'^kategoria/(?P<category_slug>[\w-]+(/[\w-]+)*)/$',
                self.category_view.as_view()),
            url(r'^ranges/(?P<slug>[\w-]+)/$',
                self.range_view.as_view(), name='range')]
        return self.post_process_urls(urlpatterns)

application = CatalogueApplication()