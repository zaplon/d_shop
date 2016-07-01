from oscarapi.app import RESTApiApplication
from apps.api.urls import urlpatterns


class OscarRESTApiApplication(RESTApiApplication):
    def get_urls(self):
        urls = super(OscarRESTApiApplication, self).get_urls()
        return urlpatterns + urls


application = OscarRESTApiApplication()
