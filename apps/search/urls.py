from django.conf.urls import url, patterns
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'product', views.ProductViewSet)
urlpatterns = [url(r'^rest/$', views.rest_view, name='rest-view')]
