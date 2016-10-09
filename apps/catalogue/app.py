from django.conf.urls import url
from oscar.apps.catalogue.app import CatalogueApplication as CorePromotionsApplication
from .views import CatalogueView, CatalogueCategoryView, EtuiView, allegro_view


class CatalogueApplication(CorePromotionsApplication):
    etui_view = CatalogueView

    def get_urls(self):
        urlpatterns = super(CatalogueApplication, self).get_urls()
        urlpatterns += [
            url(r'^opakowania-etui-folie/', EtuiView.as_view(), name='etui'),
            url(r'^allegro/', allegro_view, name='allegro'),
            url(r'^$', CatalogueCategoryView.as_view(), name='katalog'),
            url(r'^produkt/(?P<product_slug>[\w-]*)_(?P<pk>\d+)/$',
                self.detail_view.as_view(), name='detail'),
            url(r'^(?P<category_slug>[\w-]+(/[\w-]+)*)_(?P<pk>\d+)/$',
                CatalogueCategoryView.as_view(), name='category'),
            # Fallback URL if a user chops of the last part of the URL
            url(r'^(?P<category_slug>[\w-]+(/[\w-]+)*)/$',
                CatalogueCategoryView.as_view()),
            url(r'^ranges/(?P<slug>[\w-]+)/$',
                self.range_view.as_view(), name='range')]
        return self.post_process_urls(urlpatterns)

application = CatalogueApplication()