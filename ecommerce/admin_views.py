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
    
    return render(request, 'admin/new_dashboard.html', context)


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


@staff_member_required
def admin_products(request):
    """
    Admin products management page
    """
    # Get search query
    search_query = request.GET.get('search', '')

    # Get all products with related category data
    products = Product.objects.select_related('category').filter(is_active=True)

    # Apply search filter if provided
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Order by name
    products = products.order_by('name')

    # Get categories for filtering
    categories = Category.objects.filter(is_active=True).order_by('name')

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'total_products': products.count(),
    }

    return render(request, 'admin/products.html', context)


@staff_member_required
def admin_add_product(request):
    """
    Admin add product page
    """
    from .forms import ProductForm
    from django.contrib import messages
    from django.shortcuts import redirect

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" has been added successfully!')
            return redirect('admin_products')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'categories': Category.objects.filter(is_active=True).order_by('name'),
    }

    return render(request, 'admin/add_product.html', context)


@staff_member_required
def admin_orders(request):
    """
    Admin orders management page
    """
    # Get search query
    search_query = request.GET.get('search', '')

    # Get all orders with related user data
    orders = Order.objects.select_related('user').all()

    # Apply search filter if provided
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )

    # Order by creation date (newest first)
    orders = orders.order_by('-created_at')

    context = {
        'orders': orders,
        'search_query': search_query,
        'total_orders': orders.count(),
    }

    return render(request, 'admin/orders.html', context)


@staff_member_required
def admin_order_detail(request, order_number):
    """
    Admin order detail page with status update functionality
    """
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages

    # Get the order with related data
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product'),
        order_number=order_number
    )

    # Handle status update
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            old_status = order.get_status_display()
            order.status = new_status
            order.save()
            messages.success(
                request,
                f'Order #{order.order_number} status updated from "{old_status}" to "{order.get_status_display()}"'
            )
            return redirect('admin_order_detail', order_number=order.order_number)

    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }

    return render(request, 'admin/order_detail.html', context)


@staff_member_required
def admin_customers(request):
    """
    Admin customers management page
    """
    from django.contrib.auth.models import User
    from django.db.models import Count, Sum, Q

    # Get search query
    search_query = request.GET.get('search', '')

    # Get all users with order statistics
    customers = User.objects.annotate(
        order_count=Count('orders', distinct=True),
        total_spent=Sum('orders__total')
    ).filter(is_staff=False)

    # Apply search filter if provided
    if search_query:
        customers = customers.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Order by registration date (newest first)
    customers = customers.order_by('-date_joined')

    # Process customer data to add location and status
    customer_data = []
    for customer in customers:
        # Get the most recent order to determine location
        recent_order = Order.objects.filter(user=customer).order_by('-created_at').first()
        location = f"{recent_order.city}, {recent_order.state}" if recent_order and recent_order.city else "Not provided"

        # Determine status based on recent activity
        status = "Active" if customer.is_active else "Inactive"

        customer_data.append({
            'user': customer,
            'location': location,
            'order_count': customer.order_count or 0,
            'total_spent': customer.total_spent or 0,
            'status': status,
        })

    context = {
        'customers': customer_data,
        'search_query': search_query,
        'total_customers': len(customer_data),
    }

    return render(request, 'admin/customers.html', context)


@staff_member_required
def admin_logout(request):
    """
    Admin logout view
    """
    from django.contrib.auth import logout
    from django.shortcuts import redirect
    from django.contrib import messages

    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')
