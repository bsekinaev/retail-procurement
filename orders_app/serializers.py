from rest_framework import serializers
from .models import Order,  OrderItem, Contact

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product_name', 'quantity','price', 'total_price')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = ('id', 'status', 'created_at', 'items', 'total_price')


class OrderConfirmSerializer(serializers.ModelSerializer):
    contact_id = serializers.IntegerField(required=False)
    address = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
