from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Order, Product, Category

class CustomUserCreationForm(UserCreationForm):
    """
    Custom user registration form with additional fields and styling
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('username', css_class='form-group mb-3'),
            Field('email', css_class='form-group mb-3'),
            Field('password1', css_class='form-group mb-3'),
            Field('password2', css_class='form-group mb-3'),
            Submit('submit', 'Register', css_class='btn btn-primary btn-lg w-100')
        )

    def clean_email(self):
        """
        Validate that the email is unique
        """
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email address already exists.')
        return email

    def save(self, commit=True):
        """
        Save user with additional fields
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom login form with crispy forms styling
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-group mb-3'),
            Field('password', css_class='form-group mb-3'),
            Submit('submit', 'Login', css_class='btn btn-primary btn-lg w-100')
        )


class CheckoutForm(forms.ModelForm):
    """
    Checkout form for order placement
    """
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
        initial='cod',
        label='Payment Method'
    )

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country',
            'payment_method'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Field('address_line_1', css_class='form-group mb-3'),
            Field('address_line_2', css_class='form-group mb-3'),
            Row(
                Column('city', css_class='form-group col-md-4 mb-3'),
                Column('state', css_class='form-group col-md-4 mb-3'),
                Column('postal_code', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Field('country', css_class='form-group mb-3'),
            Field('payment_method', css_class='form-group mb-4'),
            Submit('submit', 'Place Order', css_class='btn btn-success btn-lg w-100')
        )


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form with enhanced styling
    """
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('email', css_class='form-group mb-3'),
            Submit('submit', 'Send Reset Link', css_class='btn btn-primary btn-lg w-100')
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("No active user found with this email address.")
        return email


class UsernameRecoveryForm(forms.Form):
    """
    Form for username recovery using email
    """
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        }),
        help_text="Enter the email address associated with your account."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('email', css_class='form-group mb-3'),
            Submit('submit', 'Recover Username', css_class='btn btn-primary btn-lg w-100')
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("No active user found with this email address.")
        return email

    def get_users(self, email):
        """
        Return all users with the given email address
        """
        return User.objects.filter(email__iexact=email, is_active=True)


class ProductForm(forms.ModelForm):
    """
    Form for adding and editing products in admin
    """
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'discount_price', 'stock', 'image', 'is_active', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter product description'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'discount_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00 (optional)'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values
        self.fields['is_active'].initial = True
        self.fields['is_featured'].initial = False

        # Make category queryset only active categories
        self.fields['category'].queryset = Category.objects.filter(is_active=True)

        # Add help text
        self.fields['discount_price'].help_text = 'Leave empty if no discount'
        self.fields['is_featured'].help_text = 'Featured products appear on homepage'

    def clean_discount_price(self):
        """
        Validate that discount price is less than regular price
        """
        discount_price = self.cleaned_data.get('discount_price')
        price = self.cleaned_data.get('price')

        if discount_price and price and discount_price >= price:
            raise ValidationError('Discount price must be less than regular price.')

        return discount_price

    def clean_image(self):
        """
        Validate image file size and type
        """
        image = self.cleaned_data.get('image')

        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file size must be less than 5MB.')

            # Check file type
            if not image.content_type.startswith('image/'):
                raise ValidationError('Please upload a valid image file.')

        return image

    def save(self, commit=True):
        """
        Save the product with auto-generated slug
        """
        product = super().save(commit=False)

        # Auto-generate slug from name if not provided
        if not product.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(product.name)
            product.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"

        if commit:
            product.save()

        return product
