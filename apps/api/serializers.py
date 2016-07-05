from oscarapi.utils import OscarHyperlinkedModelSerializer
from oscar.core.loading import get_model
from rest_framework.serializers import ModelSerializer


Product = get_model('catalogue', 'Product')
ProductImage = get_model('catalogue', 'ProductImage')


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['orginal', 'display_order', 'caption']


class ProductSerializer(OscarHyperlinkedModelSerializer):
    images = ProductImageSerializer(many=True)
    class Meta:
        model = Product
        fields = ['url', 'id', 'title', 'images']