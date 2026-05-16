from rest_framework import serializers
from .models import Product, ProductCharacteristic, Category


class ProductCharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCharacteristic
        fields = ('name', 'value')


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    supplier = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'quantity', 'is_available', 'category', 'supplier')

class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    supplier = serializers.StringRelatedField()
    characteristics = ProductCharacteristicSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description',
                  'price', 'quantity', 'is_available',
                  'category', 'supplier', 'characteristics',
                  'created_at', 'updated_at'
                  )
