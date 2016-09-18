from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = patterns(
     '',
     url(r'^products/$', views.ProductList.as_view(),
         name='product-list'),
     url(r'^available_attributes/$', views.get_available_attributes,
         name='available-attributes'),    
         
)

urlpatterns = format_suffix_patterns(urlpatterns)
