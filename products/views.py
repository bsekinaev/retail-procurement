from rest_framework import generics, filters
from .models import Product
from .serializers import ProductListSerializer,ProductDetailSerializer


class ProductListView(generics.ListAPIView):
    # Список товаров с фильтром и поиском
    serializer_class = ProductListSerializer
    queryset = Product.objects.filter(is_available=True).select_related('category','supplier')

    # Фильтрация и поиск
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'created_at']
    ordering = ['name']

    # Допольнительная фильтрация
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            is_available=True,
            supplier__is_active=True
        )
        # Применяем дополнительные фильтры из запроса
        category = self.request.query_params.get('category')
        supplier = self.request.query_params.get('supplier')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if category:
            queryset = queryset.filter(category__name__iexact=category)
        if supplier:
            queryset = queryset.filter(supplier__company_name__iexact=supplier)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset

class ProductDetailView(generics.RetrieveAPIView):
    # Детали товара
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.filter(is_available=True).prefetch_related('characteristics')
