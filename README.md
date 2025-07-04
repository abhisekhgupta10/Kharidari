# NepalShop - Django Ecommerce Application

A modern, responsive Django ecommerce application for Nepal with SQLite database, featuring secure authentication, shopping cart functionality, and a clean admin interface. All prices are in Nepali Rupees (NPR).

## Features

### 🛍️ Core Ecommerce Features
- **Product Management**: Categories, products with images, pricing, and inventory
- **Shopping Cart**: Add/remove items, update quantities, persistent cart for authenticated users
- **Order Management**: Complete checkout process, order history, order tracking
- **User Authentication**: Registration, login/logout, secure password handling

### 🎨 Modern UI/UX
- **Responsive Design**: Mobile-first approach using Bootstrap 5
- **Modern Styling**: Custom CSS with gradients, animations, and hover effects
- **Interactive Elements**: AJAX cart updates, loading states, success messages
- **Accessibility**: Proper ARIA labels, keyboard navigation, screen reader support

### 🔒 Security Features
- **CSRF Protection**: All forms protected against CSRF attacks
- **Secure Sessions**: HTTPOnly and secure session cookies
- **XSS Protection**: Content type nosniff and XSS filtering
- **Password Validation**: Strong password requirements
- **HTTPS Ready**: Security headers configured for production

### 📱 Device Responsive
- **Mobile Optimized**: Touch-friendly interface for mobile devices
- **Tablet Support**: Optimized layouts for tablet screens
- **Desktop Experience**: Full-featured desktop interface
- **Cross-browser**: Compatible with modern browsers

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Quick Start

1. **Clone or download the project**
   ```bash
   cd your-project-directory
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django pillow django-crispy-forms crispy-bootstrap5
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create sample data**
   ```bash
   python manage.py populate_data
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Nepal-Specific Features

### 🇳🇵 **Localized for Nepal**
- **Currency**: All prices displayed in Nepali Rupees (Rs.)
- **Tax Rate**: 13% VAT (Nepal standard rate)
- **Shipping**: Free shipping on orders over Rs. 5,000
- **Contact**: Nepal phone number format (+977)
- **Location**: Kathmandu, Nepal address

## Default Accounts

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Access**: Full admin panel access

### Test User Account
- **Username**: testuser
- **Password**: testpass123
- **Access**: Regular user account for testing

## Project Structure

```
ecommerce_project/
├── ecommerce/                 # Main app
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── forms.py              # Form definitions
│   ├── admin.py              # Admin configuration
│   ├── urls.py               # URL patterns
│   └── management/           # Custom management commands
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── ecommerce/           # App-specific templates
│   └── registration/        # Auth templates
├── static/                   # Static files
│   ├── css/                 # Custom CSS
│   └── js/                  # Custom JavaScript
├── media/                    # User uploaded files
├── ecommerce_project/        # Project settings
└── manage.py                # Django management script
```

## Key Models

### Product
- Name, description, price, discount price
- Category association, stock management
- Image upload, featured products
- SEO-friendly slugs

### Category
- Hierarchical organization
- Image support, descriptions
- Active/inactive status

### Cart & CartItem
- User-specific shopping carts
- Quantity management
- Price calculations

### Order & OrderItem
- Complete order processing
- Billing and shipping information
- Order status tracking
- Order history

## Admin Features

- **Product Management**: Add/edit products, manage inventory
- **Order Management**: View orders, update status, track sales
- **User Management**: Manage customer accounts
- **Category Management**: Organize product categories
- **Rich Interface**: Image previews, inline editing, filters

## Technology Stack

- **Backend**: Django 5.2.3
- **Database**: SQLite (development)
- **Frontend**: Bootstrap 5, jQuery
- **Forms**: Django Crispy Forms with Bootstrap 5
- **Icons**: Font Awesome 6
- **Images**: Pillow for image processing

## Security Considerations

- All user inputs are validated and sanitized
- CSRF tokens on all forms
- Secure session configuration
- XSS protection headers
- SQL injection prevention through Django ORM
- Password hashing with Django's built-in system

## Customization

### Adding New Features
1. Create new models in `ecommerce/models.py`
2. Add corresponding views in `ecommerce/views.py`
3. Create templates in `templates/ecommerce/`
4. Update URL patterns in `ecommerce/urls.py`

### Styling Changes
- Modify `static/css/style.css` for custom styles
- Update `templates/base.html` for layout changes
- Add JavaScript functionality in `static/js/main.js`

## Production Deployment

Before deploying to production:

1. **Security Settings**
   - Set `DEBUG = False`
   - Configure `ALLOWED_HOSTS`
   - Use environment variables for secrets
   - Set up proper database (PostgreSQL recommended)

2. **Static Files**
   - Configure static file serving
   - Set up media file handling
   - Use CDN for better performance

3. **Database**
   - Migrate to production database
   - Set up database backups
   - Configure connection pooling

## Support

This is a demonstration project showcasing Django ecommerce development best practices. The code includes extensive comments explaining functionality and implementation details.

## License

This project is created for educational and demonstration purposes.
