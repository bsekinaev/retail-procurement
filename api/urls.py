from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import auth_views, views
from products.views import ProductListView, ProductDetailView
from cart.views import CartView, CartItemAddView, CartItemUpdateView, CartItemDeleteView
from orders_app.views import OrderListView, OrderDetailView, OrderConfirmView
from suppliers.views import SupplierOrdersView, SupplierStatusView, SupplierImportView
from api.admin_views import change_order_status, export_products_csv
from .auth_views import LoginView, social_token_view

urlpatterns = [
    # Авторизация
    path('auth/register/', auth_views.register, name='register'),
    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Профиль
    path('user/profile/', auth_views.user_profile, name='user-profile'),
    path('auth/social/token/', social_token_view, name='social-token'),

    # Товары
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    # Корзина
    path('cart/', CartView.as_view(), name='cart-detail'),
    path('cart/items/', CartItemAddView.as_view(), name='cart-item-add'),
    path('cart/items/<int:pk>/', CartItemUpdateView.as_view(), name='cart-item-update'),
    path('cart/items/<int:pk>/delete/', CartItemDeleteView.as_view(), name='cart-item-delete'),

    # Заказы
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/confirm/', OrderConfirmView.as_view(), name='order-confirm'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),

    # Поставщики
    path('supplier/orders/', SupplierOrdersView.as_view(), name='supplier-orders'),
    path('supplier/status/', SupplierStatusView.as_view(), name='supplier-status'),
    path('supplier/import/', SupplierImportView.as_view(), name='supplier-import'),

    # Подтверждение email
    path('auth/verify-email/', auth_views.verify_email, name='verify-email'),

    # Админ
    path('admin/orders/<int:order_id>/', change_order_status, name='admin-change-order-status'),
    path('admin/export/csv/', export_products_csv, name='admin-export-csv'),

    # Glitchtip
    path('crash/', views.crash_test),
]