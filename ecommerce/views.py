from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from decimal import Decimal
from functools import wraps
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User



from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CheckoutForm, CustomPasswordResetForm, UsernameRecoveryForm

# Create your views here.

def customer_only(view_func):
    """
    Decorator to prevent admin/staff users from accessing customer-only features
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.is_staff):
            messages.warning(request, 'Admin users cannot access customer features. Please use the admin panel.')
            return redirect('/admin/')
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request):
    """
    Home page view with featured products and categories
    """
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'ecommerce/home.html', context)


class ProductListView(ListView):
    """
    Product listing view with search and filtering
    """
    model = Product
    template_name = 'ecommerce/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Category filtering
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)

        # Add current category if filtering by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)

        return context


class ProductDetailView(DetailView):
    """
    Product detail view
    """
    model = Product
    template_name = 'ecommerce/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add related products from same category
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:4]
        return context


class CustomLoginView(LoginView):
    """
    Custom login view with crispy forms
    """
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, 'You have been logged in successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


def custom_logout_view(request):
    """
    Simple logout view that accepts both GET and POST
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully!')
    return redirect('home')


class CustomLogoutView(LogoutView):
    """
    Custom logout view with message
    """
    http_method_names = ['get', 'post']  # Allow both GET and POST

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, 'You have been logged out successfully!')
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    """
    User registration view
    """
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)

        # Log the user in after successful registration
        login(self.request, self.object)

        # Send welcome email
        try:
            subject = f'Welcome to Kharidari - Your Account is Ready!'
            html_message = render_to_string('emails/welcome_email.html', {
                'user': self.object,
                'site_name': 'Kharidari',
                'request': self.request,
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.object.email],
                html_message=html_message,
                fail_silently=True,  # Don't fail registration if email fails
            )

            messages.success(
                self.request,
                f'Account created successfully! Welcome to Kharidari, {self.object.first_name or self.object.username}! '
                f'A welcome email has been sent to {self.object.email}.'
            )
        except Exception as e:
            # Log the error but don't fail the registration
            print(f"Failed to send welcome email: {e}")
            messages.success(self.request, 'Account created successfully! Welcome to Kharidari!')

        return response

    def form_invalid(self, form):
        # Add specific error messages for common issues
        if 'email' in form.errors:
            for error in form.errors['email']:
                messages.error(self.request, f"Email Error: {error}")

        if 'username' in form.errors:
            for error in form.errors['username']:
                messages.error(self.request, f"Username Error: {error}")

        if 'password2' in form.errors:
            for error in form.errors['password2']:
                messages.error(self.request, f"Password Error: {error}")

        return super().form_invalid(form)


@login_required
@customer_only
def cart_view(request):
    """
    Display user's shopping cart
    """
    cart, _ = Cart.objects.get_or_create(user=request.user)
    context = {
        'cart': cart,
    }
    return render(request, 'ecommerce/cart.html', context)


@login_required
@customer_only
@require_POST
def add_to_cart(request, product_id):
    """
    Add product to cart via AJAX
    """
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get quantity from request
    quantity = int(request.POST.get('quantity', 1))

    # Check if product is in stock
    if quantity > product.stock:
        return JsonResponse({
            'success': False,
            'message': f'Only {product.stock} items available in stock.'
        })

    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        # Update quantity if item already exists
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            return JsonResponse({
                'success': False,
                'message': f'Cannot add more items. Only {product.stock} available in stock.'
            })
        cart_item.quantity = new_quantity
        cart_item.save()

    return JsonResponse({
        'success': True,
        'message': f'{product.name} added to cart!',
        'cart_total_items': cart.total_items,
        'cart_total_price': float(cart.total_price)
    })


@login_required
@customer_only
@require_POST
def update_cart_item(request, item_id):
    """
    Update cart item quantity via AJAX
    """
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart.',
            'cart_total_items': cart_item.cart.total_items,
            'cart_total_price': float(cart_item.cart.total_price)
        })

    if quantity > cart_item.product.stock:
        return JsonResponse({
            'success': False,
            'message': f'Only {cart_item.product.stock} items available in stock.'
        })

    cart_item.quantity = quantity
    cart_item.save()

    return JsonResponse({
        'success': True,
        'message': 'Cart updated successfully!',
        'item_total': float(cart_item.get_total_price()),
        'cart_total_items': cart_item.cart.total_items,
        'cart_total_price': float(cart_item.cart.total_price)
    })


@login_required
@customer_only
@require_POST
def remove_from_cart(request, item_id):
    """
    Remove item from cart via AJAX
    """
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()

    return JsonResponse({
        'success': True,
        'message': 'Item removed from cart.',
        'cart_total_items': cart_item.cart.total_items,
        'cart_total_price': float(cart_item.cart.total_price)
    })


@login_required
@customer_only
def checkout_view(request):
    """
    Checkout process view
    """
    cart = get_object_or_404(Cart, user=request.user)

    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = request.user
            order.subtotal = cart.total_price
            order.tax = cart.total_price * Decimal('0.13')  # 13% VAT (Nepal standard)
            order.shipping = Decimal('200.00') if cart.total_price < Decimal('5000.00') else Decimal('0.00')  # Free shipping over Rs. 5000
            order.total = order.subtotal + order.tax + order.shipping
            order.save()

            # Create order items and update product stock
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.get_price
                )
                # Update product stock
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()

            # Clear cart
            cart.items.all().delete()

            # Send order confirmation email
            try:
                subject = f'Order Confirmation #{order.order_number} - Kharidari'
                html_message = render_to_string('emails/order_confirmation_email.html', {
                    'order': order,
                    'site_name': 'Kharidari',
                    'user': request.user,
                })
                plain_message = strip_tags(html_message)

                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[order.email],
                    html_message=html_message,
                    fail_silently=True,  # Don't fail the order if email fails
                )

                messages.success(request, f'Order {order.order_number} placed successfully! A confirmation email has been sent to {order.email}.')
            except Exception as e:
                # Log the error but don't fail the order
                print(f"Failed to send order confirmation email: {e}")
                messages.success(request, f'Order {order.order_number} placed successfully!')

            return redirect('order_detail', order_number=order.order_number)
    else:
        # Pre-fill form with user data
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'ecommerce/checkout.html', context)


@login_required
@customer_only
def order_detail_view(request, order_number):
    """
    Order detail view
    """
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'ecommerce/order_detail.html', context)


@login_required
@customer_only
def order_history_view(request):
    """
    User's order history
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'ecommerce/order_history.html', context)


def forgot_password_view(request):
    """
    Password reset request view with actual email sending
    """
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                # Get user with this email
                user = User.objects.get(email=email, is_active=True)

                # Generate password reset token (simplified for demo)
                # In production, use Django's built-in password reset tokens
                import secrets
                reset_token = secrets.token_urlsafe(32)

                # Store token in session for demo (in production, use database or cache)
                request.session[f'reset_token_{user.id}'] = reset_token
                request.session[f'reset_email_{user.id}'] = email

                # Create reset URL
                reset_url = request.build_absolute_uri(f'/reset-password/{user.id}/{reset_token}/')

                # Prepare email content
                subject = 'Password Reset Request - Kharidari'

                # HTML email content
                html_message = render_to_string('emails/password_reset_email.html', {
                    'user': user,
                    'reset_url': reset_url,
                    'site_name': 'Kharidari',
                })

                # Plain text version
                plain_message = strip_tags(html_message)

                # Send email
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )

                messages.success(
                    request,
                    f'Password reset instructions have been sent to {email}. '
                    f'Please check your email and follow the instructions to reset your password.'
                )
                return redirect('login')

            except User.DoesNotExist:
                # Don't reveal that the user doesn't exist for security
                messages.success(
                    request,
                    f'If an account with {email} exists, password reset instructions have been sent.'
                )
                return redirect('login')
            except Exception as e:
                messages.error(
                    request,
                    'There was an error sending the password reset email. Please try again later.'
                )
    else:
        form = CustomPasswordResetForm()

    context = {
        'form': form,
    }
    return render(request, 'registration/password_reset.html', context)


def forgot_username_view(request):
    """
    Username recovery view with actual email sending
    """
    if request.method == 'POST':
        form = UsernameRecoveryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                # Get users with this email
                users = User.objects.filter(email=email, is_active=True)

                if users.exists():
                    usernames = [user.username for user in users]

                    # Prepare email content
                    subject = 'Username Recovery - Kharidari'

                    # HTML email content
                    html_message = render_to_string('emails/username_recovery_email.html', {
                        'usernames': usernames,
                        'email': email,
                        'site_name': 'Kharidari',
                    })

                    # Plain text version
                    plain_message = strip_tags(html_message)

                    # Send email
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    messages.success(
                        request,
                        f'Your username information has been sent to {email}. '
                        f'Please check your email for your account details.'
                    )
                    return redirect('login')
                else:
                    # Don't reveal that no user exists for security
                    messages.success(
                        request,
                        f'If an account with {email} exists, username information has been sent.'
                    )
                    return redirect('login')

            except Exception as e:
                messages.error(
                    request,
                    'There was an error sending the username recovery email. Please try again later.'
                )
    else:
        form = UsernameRecoveryForm()

    context = {
        'form': form,
    }
    return render(request, 'registration/username_recovery.html', context)


def account_recovery_view(request):
    """
    Account recovery options view
    """
    return render(request, 'registration/account_recovery.html')


def password_reset_confirm_view(request, user_id, token):
    """
    Password reset confirmation view
    """
    try:
        user = User.objects.get(id=user_id, is_active=True)

        # Check if token is valid (from session)
        session_token = request.session.get(f'reset_token_{user_id}')
        # session_email = request.session.get(f'reset_email_{user_id}')  # For future use

        if not session_token or session_token != token:
            messages.error(request, 'Invalid or expired password reset link.')
            return redirect('forgot_password')

        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not new_password or not confirm_password:
                messages.error(request, 'Please fill in all fields.')
            elif new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
            else:
                # Set new password
                user.set_password(new_password)
                user.save()

                # Clear session tokens
                if f'reset_token_{user_id}' in request.session:
                    del request.session[f'reset_token_{user_id}']
                if f'reset_email_{user_id}' in request.session:
                    del request.session[f'reset_email_{user_id}']

                # Send confirmation email
                try:
                    subject = 'Password Successfully Reset - NepalShop'
                    html_message = render_to_string('emails/password_reset_success_email.html', {
                        'user': user,
                        'site_name': 'Kharidari',
                    })
                    plain_message = strip_tags(html_message)

                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=True,
                    )
                except:
                    pass  # Don't fail if confirmation email fails

                messages.success(
                    request,
                    'Your password has been successfully reset! You can now log in with your new password.'
                )
                return redirect('login')

        context = {
            'user': user,
            'token': token,
        }
        return render(request, 'registration/password_reset_confirm.html', context)

    except User.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('forgot_password')


def custom_404_view(request, exception=None):
    """
    Custom 404 error page view
    """
    return render(request, '404.html', status=404)


def custom_500_view(request):
    """
    Custom 500 error page view
    """
    return render(request, '500.html', status=500)


def test_404_view(request):
    """
    Test view to demonstrate 404 page (for development)
    """
    from django.http import Http404
    raise Http404("This is a test 404 page")


def serve_media(request, path):
    """
    Custom media serving view for production/ngrok
    """
    import os
    import mimetypes
    from django.http import Http404, HttpResponse
    from django.conf import settings

    try:
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # Get the content type
            content_type, _ = mimetypes.guess_type(file_path)

            # Open and serve the file
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
                return response
        else:
            raise Http404("Media file not found")
    except Exception as e:
        # Log the error for debugging
        print(f"Error serving media file {path}: {e}")
        raise Http404("Media file not found")


def debug_media_view(request):
    """
    Debug view to check media files and paths
    """
    import os
    from django.conf import settings
    from django.http import JsonResponse

    media_root = settings.MEDIA_ROOT
    media_url = settings.MEDIA_URL

    # List all files in media directory
    media_files = []
    if os.path.exists(media_root):
        for root, _, files in os.walk(media_root):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, media_root)
                media_files.append({
                    'file': relative_path,
                    'full_path': file_path,
                    'url': f"{media_url}{relative_path}",
                    'exists': os.path.exists(file_path),
                    'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
                })

    debug_info = {
        'media_root': str(media_root),
        'media_url': media_url,
        'media_root_exists': os.path.exists(media_root),
        'debug_mode': settings.DEBUG,
        'files_count': len(media_files),
        'files': media_files[:10],  # Show first 10 files
    }

    return JsonResponse(debug_info, indent=2)
