from oscarapi.utils import OscarHyperlinkedModelSerializer
from oscar.core.loading import get_model


Product = get_model('catalogue', 'Product')


class ProductLinkSerializer(OscarHyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ['url', 'id', 'title']