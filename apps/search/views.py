from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.api.serializers import ProductElasticSerializer
from oscar.core.loading import get_model


Product = get_model('catalogue', 'Product')


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductElasticSerializer
