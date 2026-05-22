from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from users.views import social_complete

urlpatterns = [
    path('baton/', include('baton.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('auth/social/', include('social_django.urls', namespace='social')),

    # Swagger
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Frontend
    path('', TemplateView.as_view(template_name='login.html'), name='login-page'),
    path('login.html', TemplateView.as_view(template_name='login.html'), name='login-page-alt'),
    path('register.html', TemplateView.as_view(template_name='register.html'), name='register-page'),
    path('index.html', TemplateView.as_view(template_name='index.html'), name='index-page'),
    path('cart.html', TemplateView.as_view(template_name='cart.html'), name='cart-page'),
    path('orders.html', TemplateView.as_view(template_name='orders.html'), name='orders-page'),



]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)