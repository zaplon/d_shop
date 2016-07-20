from oscarapi.utils import OscarHyperlinkedModelSerializer
from oscar.core.loading import get_model
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import CharField


Product = get_model('catalogue', 'Product')
ProductImage = get_model('catalogue', 'ProductImage')


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['original', 'display_order', 'caption']


class ProductSerializer(OscarHyperlinkedModelSerializer):
    images = ProductImageSerializer(many=True)
    front_url = CharField(read_only=True, source='get_absolute_url')
    class Meta:
        model = Product
        fields = ['url', 'id', 'title', 'images', 'front_url']