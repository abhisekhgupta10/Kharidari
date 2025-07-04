from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ecommerce.models import Category, Product
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create categories
        categories_data = [
            {
                'name': 'Electronics',
                'slug': 'electronics',
                'description': 'Latest electronic gadgets and devices'
            },
            {
                'name': 'Clothing',
                'slug': 'clothing',
                'description': 'Fashion and apparel for all occasions'
            },
            {
                'name': 'Books',
                'slug': 'books',
                'description': 'Books, magazines, and educational materials'
            },
            {
                'name': 'Home & Garden',
                'slug': 'home-garden',
                'description': 'Home improvement and garden supplies'
            },
            {
                'name': 'Sports',
                'slug': 'sports',
                'description': 'Sports equipment and fitness gear'
            },
            {
                'name': 'Beauty',
                'slug': 'beauty',
                'description': 'Beauty and personal care products'
            }
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create products with Nepali Rupee prices
        products_data = [
            {
                'name': 'Wireless Bluetooth Headphones',
                'slug': 'wireless-bluetooth-headphones',
                'description': 'High-quality wireless headphones with noise cancellation and long battery life.',
                'price': Decimal('12999.00'),
                'discount_price': Decimal('9999.00'),
                'category': 'electronics',
                'stock': 50,
                'is_featured': True
            },
            {
                'name': 'Smartphone Case',
                'slug': 'smartphone-case',
                'description': 'Protective case for smartphones with shock absorption and wireless charging compatibility.',
                'price': Decimal('2999.00'),
                'category': 'electronics',
                'stock': 100,
                'is_featured': False
            },
            {
                'name': 'Cotton T-Shirt',
                'slug': 'cotton-t-shirt',
                'description': 'Comfortable 100% cotton t-shirt available in multiple colors and sizes.',
                'price': Decimal('2499.00'),
                'discount_price': Decimal('1899.00'),
                'category': 'clothing',
                'stock': 75,
                'is_featured': True
            },
            {
                'name': 'Denim Jeans',
                'slug': 'denim-jeans',
                'description': 'Classic fit denim jeans made from premium quality denim fabric.',
                'price': Decimal('7999.00'),
                'category': 'clothing',
                'stock': 30,
                'is_featured': False
            },
            {
                'name': 'Programming Book',
                'slug': 'programming-book',
                'description': 'Comprehensive guide to modern programming languages and best practices.',
                'price': Decimal('4999.00'),
                'category': 'books',
                'stock': 25,
                'is_featured': True
            },
            {
                'name': 'Cooking Recipe Book',
                'slug': 'cooking-recipe-book',
                'description': 'Collection of delicious recipes from around the world with step-by-step instructions.',
                'price': Decimal('3999.00'),
                'category': 'books',
                'stock': 40,
                'is_featured': False
            },
            {
                'name': 'Garden Tool Set',
                'slug': 'garden-tool-set',
                'description': 'Complete set of essential gardening tools for maintaining your garden.',
                'price': Decimal('9999.00'),
                'discount_price': Decimal('8499.00'),
                'category': 'home-garden',
                'stock': 20,
                'is_featured': True
            },
            {
                'name': 'Indoor Plant Pot',
                'slug': 'indoor-plant-pot',
                'description': 'Decorative ceramic pot perfect for indoor plants with drainage system.',
                'price': Decimal('1999.00'),
                'category': 'home-garden',
                'stock': 60,
                'is_featured': False
            },
            {
                'name': 'Yoga Mat',
                'slug': 'yoga-mat',
                'description': 'Non-slip yoga mat with extra cushioning for comfortable workouts.',
                'price': Decimal('4299.00'),
                'category': 'sports',
                'stock': 45,
                'is_featured': True
            },
            {
                'name': 'Water Bottle',
                'slug': 'water-bottle',
                'description': 'Insulated stainless steel water bottle that keeps drinks cold for 24 hours.',
                'price': Decimal('2899.00'),
                'category': 'sports',
                'stock': 80,
                'is_featured': False
            },
            {
                'name': 'Face Moisturizer',
                'slug': 'face-moisturizer',
                'description': 'Hydrating face moisturizer with SPF protection for daily use.',
                'price': Decimal('3699.00'),
                'discount_price': Decimal('2999.00'),
                'category': 'beauty',
                'stock': 35,
                'is_featured': True
            },
            {
                'name': 'Lip Balm Set',
                'slug': 'lip-balm-set',
                'description': 'Set of 3 natural lip balms with different flavors for soft, smooth lips.',
                'price': Decimal('1599.00'),
                'category': 'beauty',
                'stock': 90,
                'is_featured': False
            }
        ]
        
        for prod_data in products_data:
            category = categories[prod_data.pop('category')]
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={**prod_data, 'category': category}
            )
            if created:
                self.stdout.write(f'Created product: {product.name}')
        
        # Create a test user
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write('Created test user: testuser (password: testpass123)')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
        self.stdout.write('Admin user: admin (password: admin123)')
        self.stdout.write('Test user: testuser (password: testpass123)')
