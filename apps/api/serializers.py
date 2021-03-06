# encoding: utf-8
from oscarapi.utils import OscarModelSerializer, OscarHyperlinkedModelSerializer
from oscar.core.loading import get_model
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer
from rest_framework.fields import CharField, IntegerField, SerializerMethodField, FloatField, JSONField
from oscar.apps.partner.strategy import Selector


Product = get_model('catalogue', 'Product')
ProductImage = get_model('catalogue', 'ProductImage')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
Category = get_model('catalogue', 'Category')
StockRecord = get_model('partner', 'StockRecord')


class StockRecordSerializer(ModelSerializer):
    price = FloatField(source='price_retail')
    class Meta:
        model = StockRecord
        fields = ['price_excl_tax', 'price', 'num_in_stock', 'is_available']


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['original', 'display_order', 'caption']


class ProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many=True)
    front_url = CharField(read_only=True, source='get_absolute_url')
    sell_details = SerializerMethodField()

    def get_sell_details(self, obj):
        selector = Selector()
        strategy = selector.strategy(request=self.context['request'], user=self.context['request'].user)
        purchase_info = strategy.fetch_for_product(product=obj)
        price = purchase_info.price
        return {'is_available': strategy.select_stockrecord(obj).num_in_stock > 0,
                'price': {'retail': str(purchase_info.stockrecord.price_retail).replace('.', ',') + u' zł'}}

    class Meta:
        model = Product
        fields = ['url', 'id', 'title', 'images', 'front_url', 'sell_details']


class ProductAttributeValueSerializer(ModelSerializer):
    name = CharField(source='attribute.name')
    #combined = CharField(source='get_combined')
    class Meta:
        model = ProductAttributeValue
        fields = ['value', 'name', 'slug', 'id']


class CategorySerializer(ModelSerializer):
    ids = CharField(source='get_ids')
    class Meta:
        model = Category
        fields = ['name', 'full_name', 'id', 'ids']


class ProductElasticSerializer(ModelSerializer):
    images = ProductImageSerializer(many=True)
    stockrecords = StockRecordSerializer(many=True)
    type = CharField(source='product_class.external_type')
    attribute_values = ProductAttributeValueSerializer(many=True)
    categories = CategorySerializer(many=True)
    front_url = CharField(source='get_absolute_url')
    query_suggest = JSONField(source='get_query_suggestions')
    #_id = CharField(source='external_id')

    class Meta:
        model = Product
        fields = ['id', 'front_url', 'title', 'images', 'stockrecords', 'description', 'type', 'attribute_values',
                  'categories', 'query_suggest']
