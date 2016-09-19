from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = patterns(
     '',
     url(r'^products/$', views.ProductList.as_view(),
         name='product-list')
         
)

urlpatterns = format_suffix_patterns(urlpatterns)
