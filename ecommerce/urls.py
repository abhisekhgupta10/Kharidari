from django.urls import path
from . import views

urlpatterns = [
    # Home and product views
    path('', views.home, name='home'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/category/<slug:category_slug>/', views.ProductListView.as_view(), name='category_products'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Authentication views
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Account recovery views
    path('account-recovery/', views.account_recovery_view, name='account_recovery'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('forgot-username/', views.forgot_username_view, name='forgot_username'),
    path('reset-password/<int:user_id>/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # Cart views
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Order views
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('orders/', views.order_history_view, name='order_history'),

    # Test 404 page (for development testing)
    path('test-404/', views.test_404_view, name='test_404'),

    # Debug media files (for development testing)
    path('debug-media/', views.debug_media_view, name='debug_media'),
]
