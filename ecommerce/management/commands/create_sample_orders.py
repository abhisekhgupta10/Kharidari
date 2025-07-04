from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ecommerce.models import Product, Order, OrderItem
from decimal import Decimal
import random
from datetime import datetime, timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create sample orders for dashboard analytics'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample orders...')
        
        # Get test user
        try:
            test_user = User.objects.get(username='testuser')
        except User.DoesNotExist:
            self.stdout.write('Test user not found. Creating one...')
            test_user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='Customer'
            )
        
        # Create additional test customers
        customers = [test_user]
        for i in range(5):
            username = f'customer{i+1}'
            try:
                customer = User.objects.get(username=username)
            except User.DoesNotExist:
                customer = User.objects.create_user(
                    username=username,
                    email=f'customer{i+1}@example.com',
                    password='testpass123',
                    first_name=f'Customer',
                    last_name=f'{i+1}'
                )
            customers.append(customer)
        
        # Get all products
        products = list(Product.objects.filter(is_active=True))
        if not products:
            self.stdout.write('No products found. Please run populate_data first.')
            return
        
        # Order statuses
        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        
        # Create orders for the last 60 days
        orders_created = 0
        for days_ago in range(60):
            # Create 1-3 orders per day
            num_orders = random.randint(1, 3)
            
            for _ in range(num_orders):
                # Random customer
                customer = random.choice(customers)
                
                # Random date
                order_date = timezone.now() - timedelta(days=days_ago)
                order_date = order_date.replace(
                    hour=random.randint(9, 21),
                    minute=random.randint(0, 59)
                )
                
                # Create order
                order = Order.objects.create(
                    user=customer,
                    first_name=customer.first_name,
                    last_name=customer.last_name,
                    email=customer.email,
                    phone=f'+977-98{random.randint(10000000, 99999999)}',
                    address_line_1=f'{random.randint(1, 999)} Random Street',
                    city='Kathmandu',
                    state='Bagmati',
                    postal_code=f'{random.randint(10000, 99999)}',
                    country='Nepal',
                    status=random.choice(statuses),
                    subtotal=Decimal('0'),
                    tax=Decimal('0'),
                    shipping=Decimal('0'),
                    total=Decimal('0'),
                    created_at=order_date,
                    updated_at=order_date
                )
                
                # Add 1-5 random products to order
                num_items = random.randint(1, 5)
                order_total = Decimal('0')
                
                for _ in range(num_items):
                    product = random.choice(products)
                    quantity = random.randint(1, 3)
                    price = product.discount_price if product.discount_price else product.price
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=price
                    )
                    
                    order_total += price * quantity
                
                # Calculate totals
                order.subtotal = order_total
                order.tax = order_total * Decimal('0.13')  # 13% VAT
                order.shipping = Decimal('200') if order_total < Decimal('5000') else Decimal('0')
                order.total = order.subtotal + order.tax + order.shipping
                order.save()
                
                orders_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {orders_created} sample orders!')
        )
