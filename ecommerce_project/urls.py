"""
URL configuration for ecommerce_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from ecommerce.admin_views import admin_dashboard, sales_analytics, admin_products, admin_add_product, admin_orders, admin_order_detail, admin_customers, admin_logout
from ecommerce.admin import admin_site
from ecommerce import views

# Custom admin URLs
admin_patterns = [
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('orders/', admin_orders, name='admin_orders'),
    path('orders/<str:order_number>/', admin_order_detail, name='admin_order_detail'),
    path('customers/', admin_customers, name='admin_customers'),
    path('products/', admin_products, name='admin_products'),
    path('products/add/', admin_add_product, name='admin_add_product'),
    path('analytics/', sales_analytics, name='admin_analytics'),
    path('logout/', admin_logout, name='admin_logout'),
    path('', admin_site.urls),
]

urlpatterns = [
    path('admin/', include(admin_patterns)),
    path('', include('ecommerce.urls')),
    # Custom media serving for ngrok/production
    re_path(r'^media/(?P<path>.*)$', views.serve_media, name='serve_media'),
]

# Custom error handlers
handler404 = 'ecommerce.views.custom_404_view'
handler500 = 'ecommerce.views.custom_500_view'

# Serve static and media files
# For ngrok/development deployment, serve media files even when DEBUG = False
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
