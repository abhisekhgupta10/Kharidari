from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
import json
from decimal import Decimal

from .models import Product, Category, Order, OrderItem


@staff_member_required
def admin_dashboard(request):
    """
    Custom admin dashboard with analytics and charts
    """
    # Get date range for analytics (last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Basic statistics
    total_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    total_customers = Order.objects.values('user').distinct().count()
    
    # Revenue statistics
    total_revenue = Order.objects.aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')
    
    monthly_revenue = Order.objects.filter(
        created_at__gte=start_date
    ).aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')
    
    # Average order value
    avg_order_value = Order.objects.aggregate(
        avg=Avg('total')
    )['avg'] or Decimal('0')
    
    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Top selling products
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).filter(
        total_sold__isnull=False
    ).order_by('-total_sold')[:10]
    
    # Orders by status
    order_status_data = []
    status_counts = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    for status in status_counts:
        order_status_data.append({
            'status': status['status'].title(),
            'count': status['count']
        })
    
    # Daily sales for the last 30 days
    daily_sales = Order.objects.filter(
        created_at__date__gte=start_date
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total_sales=Sum('total'),
        order_count=Count('id')
    ).order_by('date')
    
    # Prepare chart data
    sales_chart_data = {
        'labels': [sale['date'].strftime('%Y-%m-%d') for sale in daily_sales],
        'sales': [float(sale['total_sales']) for sale in daily_sales],
        'orders': [sale['order_count'] for sale in daily_sales]
    }
    
    # Category distribution
    category_data = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).filter(is_active=True)
    
    category_chart_data = {
        'labels': [cat.name for cat in category_data],
        'data': [cat.product_count for cat in category_data]
    }
    
    # Low stock products
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock__lte=10
    ).order_by('stock')[:10]
    
    # Monthly revenue trend (last 12 months)
    twelve_months_ago = end_date - timedelta(days=365)
    monthly_trend = Order.objects.filter(
        created_at__date__gte=twelve_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        revenue=Sum('total'),
        orders=Count('id')
    ).order_by('month')
    
    monthly_trend_data = {
        'labels': [trend['month'].strftime('%Y-%m') for trend in monthly_trend],
        'revenue': [float(trend['revenue']) for trend in monthly_trend],
        'orders': [trend['orders'] for trend in monthly_trend]
    }
    
    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'avg_order_value': avg_order_value,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'order_status_data': json.dumps(order_status_data),
        'sales_chart_data': json.dumps(sales_chart_data),
        'category_chart_data': json.dumps(category_chart_data),
        'low_stock_products': low_stock_products,
        'monthly_trend_data': json.dumps(monthly_trend_data),
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def sales_analytics(request):
    """
    Detailed sales analytics page
    """
    # Get date range from request or default to last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Sales by product category
    category_sales = OrderItem.objects.filter(
        order__created_at__date__gte=start_date
    ).values(
        'product__category__name'
    ).annotate(
        total_revenue=Sum('price'),
        total_quantity=Sum('quantity')
    ).order_by('-total_revenue')

    # Add calculated fields
    category_sales_list = []
    for category in category_sales:
        category_dict = dict(category)
        if category['total_quantity'] > 0:
            category_dict['avg_price'] = category['total_revenue'] / category['total_quantity']
        else:
            category_dict['avg_price'] = 0
        category_sales_list.append(category_dict)
    
    # Top customers
    top_customers = Order.objects.filter(
        created_at__date__gte=start_date
    ).values(
        'user__username',
        'user__first_name',
        'user__last_name'
    ).annotate(
        total_spent=Sum('total'),
        order_count=Count('id')
    ).order_by('-total_spent')[:10]

    # Add calculated fields for customers
    top_customers_list = []
    for customer in top_customers:
        customer_dict = dict(customer)
        if customer['order_count'] > 0:
            customer_dict['avg_order'] = customer['total_spent'] / customer['order_count']
        else:
            customer_dict['avg_order'] = 0
        top_customers_list.append(customer_dict)
    
    context = {
        'category_sales': category_sales_list,
        'top_customers': top_customers_list,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'admin/sales_analytics.html', context)
