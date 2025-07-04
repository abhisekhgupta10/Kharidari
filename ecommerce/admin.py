from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Product, Cart, CartItem, Order, OrderItem

# Customize admin site headers and titles
admin.site.site_header = "Kharidari Administration"
admin.site.site_title = "Kharidari Admin"
admin.site.index_title = "Welcome to Kharidari Administration"

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model
    """
    list_display = ['name', 'slug', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def product_count(self, obj):
        """Display number of products in category"""
        count = obj.products.count()
        if count > 0:
            url = reverse('admin:ecommerce_product_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} products</a>', url, count)
        return '0 products'
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin configuration for Product model
    """
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_active', 'is_featured', 'image_preview']
    list_filter = ['category', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    list_editable = ['price', 'discount_price', 'stock', 'is_active', 'is_featured']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Inventory', {
            'fields': ('stock',)
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        """Display image preview in admin"""
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;">')
        return 'No image'
    image_preview.short_description = 'Image Preview'


class CartItemInline(admin.TabularInline):
    """
    Inline admin for CartItem
    """
    model = CartItem
    extra = 0
    readonly_fields = ['get_total_price']

    def get_total_price(self, obj):
        """Display total price for cart item"""
        if obj.id:
            return f'${obj.get_total_price()}'
        return '-'
    get_total_price.short_description = 'Total Price'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin configuration for Cart model
    """
    list_display = ['user', 'total_items', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'total_price']
    inlines = [CartItemInline]

    def total_items(self, obj):
        """Display total items in cart"""
        return obj.total_items
    total_items.short_description = 'Total Items'

    def total_price(self, obj):
        """Display total price of cart"""
        return f'${obj.total_price}'
    total_price.short_description = 'Total Price'


class OrderItemInline(admin.TabularInline):
    """
    Inline admin for OrderItem
    """
    model = OrderItem
    extra = 0
    readonly_fields = ['get_total_price']

    def get_total_price(self, obj):
        """Display total price for order item"""
        if obj.id:
            return f'${obj.get_total_price()}'
        return '-'
    get_total_price.short_description = 'Total Price'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for Order model
    """
    list_display = ['order_number', 'user', 'status', 'payment_method', 'total', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at', 'updated_at']
    search_fields = ['order_number', 'user__username', 'user__email', 'first_name', 'last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    list_editable = ['status']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_method')
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'tax', 'shipping', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Override save to handle order number generation"""
        super().save_model(request, obj, form, change)


# Custom admin site with dashboard data
class KharidariAdminSite(admin.AdminSite):
    site_header = 'Kharidari Administration'
    site_title = 'Kharidari Admin'
    index_title = 'Welcome to Kharidari Administration'

    def index(self, request, extra_context=None):
        """
        Custom admin index with dashboard statistics
        """
        from django.db.models import Sum, Count
        from decimal import Decimal

        extra_context = extra_context or {}

        # Add basic statistics
        extra_context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_orders': Order.objects.count(),
            'total_customers': Order.objects.values('user').distinct().count(),
            'total_revenue': Order.objects.aggregate(
                total=Sum('total')
            )['total'] or Decimal('0'),
        })

        return super().index(request, extra_context)

# Replace default admin site
admin_site = KharidariAdminSite(name='admin')

# Re-register all models with the new admin site
admin_site.register(Category, CategoryAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(Cart, CartAdmin)
admin_site.register(Order, OrderAdmin)

# Register User model
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
