from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from django.views.decorators.cache import cache_page
from django.conf import settings


urlpatterns = [
     url(r'^products/$', cache_page(settings.CACHE_PERIOD)(views.ProductList.as_view()),
         name='product-list'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
