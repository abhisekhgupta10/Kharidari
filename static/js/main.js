// Modern Ecommerce JavaScript

$(document).ready(function() {
    // Setup CSRF token for all AJAX requests
    setupCSRF();

    // Initialize all components
    initializeComponents();
    loadCartCount();
    setupEventListeners();
});

/**
 * Setup CSRF token for all AJAX requests
 */
function setupCSRF() {
    // Get CSRF token
    const csrfToken = getCsrfToken();

    // Setup jQuery to send CSRF token with all AJAX requests
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain && csrfToken) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });
}

/**
 * Initialize all JavaScript components
 */
function initializeComponents() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add fade-in animation to cards
    $('.card').addClass('fade-in');
    
    // Smooth scroll for anchor links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if( target.length ) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });
}

/**
 * Load cart count from server
 */
function loadCartCount() {
    if (isUserAuthenticated()) {
        // This would typically be an AJAX call to get cart count
        // For now, we'll update it when items are added
        updateCartCountDisplay();
    }
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Add to cart buttons
    $(document).on('click', '.add-to-cart-btn', handleAddToCart);
    
    // Search form enhancement
    $('#search-form').on('submit', function(e) {
        const searchInput = $(this).find('input[name="search"]');
        if (searchInput.val().trim() === '') {
            e.preventDefault();
            searchInput.focus();
            showMessage('warning', 'Please enter a search term');
        }
    });
    
    // Image lazy loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Form validation enhancement
    $('form').on('submit', function() {
        const form = $(this);
        const submitBtn = form.find('button[type="submit"]');
        
        // Add loading state to submit button
        if (!submitBtn.prop('disabled')) {
            const originalText = submitBtn.html();
            submitBtn.data('original-text', originalText);
            submitBtn.prop('disabled', true);
            
            // Add spinner
            const spinner = '<i class="fas fa-spinner fa-spin me-2"></i>';
            const loadingText = submitBtn.data('loading-text') || 'Processing...';
            submitBtn.html(spinner + loadingText);
            
            // Reset button after 10 seconds as fallback
            setTimeout(function() {
                if (submitBtn.prop('disabled')) {
                    submitBtn.prop('disabled', false);
                    submitBtn.html(originalText);
                }
            }, 10000);
        }
    });
    
    // Quantity input validation
    $(document).on('change', 'input[type="number"]', function() {
        const input = $(this);
        const min = parseInt(input.attr('min')) || 1;
        const max = parseInt(input.attr('max')) || 999;
        let value = parseInt(input.val());
        
        if (isNaN(value) || value < min) {
            input.val(min);
        } else if (value > max) {
            input.val(max);
            showMessage('warning', `Maximum quantity is ${max}`);
        }
    });
}

/**
 * Handle add to cart button clicks
 */
function handleAddToCart(e) {
    e.preventDefault();
    
    const btn = $(this);
    const productId = btn.data('product-id');
    const form = btn.closest('form');
    let quantity = 1;
    
    // Get quantity from form if exists
    if (form.length > 0) {
        const quantityInput = form.find('input[name="quantity"]');
        if (quantityInput.length > 0) {
            quantity = parseInt(quantityInput.val()) || 1;
        }
    }
    
    // Check if user is authenticated
    if (!isUserAuthenticated()) {
        showMessage('warning', 'Please login to add items to cart');
        return;
    }

    // Check if user is admin
    if (isUserAdmin()) {
        showMessage('info', 'Admin users cannot add items to cart. Use the admin panel to manage products.');
        return;
    }
    
    // Disable button and show loading
    const originalText = btn.html();
    btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i>Adding...');
    
    // Make AJAX request
    $.ajax({
        url: `/add-to-cart/${productId}/`,
        type: 'POST',
        data: {
            'quantity': quantity,
            'csrfmiddlewaretoken': getCsrfToken()
        },
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .done(function(data) {
        if (data.success) {
            // Update cart count
            updateCartCount(data.cart_total_items);
            
            // Show success message
            showMessage('success', data.message);
            
            // Add visual feedback
            btn.removeClass('btn-primary').addClass('btn-success');
            btn.html('<i class="fas fa-check me-1"></i>Added!');
            
            // Reset button after 2 seconds
            setTimeout(function() {
                btn.removeClass('btn-success').addClass('btn-primary');
                btn.html(originalText);
            }, 2000);
        } else {
            showMessage('danger', data.message);
        }
    })
    .fail(function() {
        showMessage('danger', 'An error occurred. Please try again.');
    })
    .always(function() {
        // Re-enable button
        btn.prop('disabled', false);
    });
}

/**
 * Show message to user
 */
function showMessage(type, message) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Remove existing alerts
    $('.alert').remove();
    
    // Add new alert to top of main content
    $('main').prepend(`<div class="container mt-3">${alertHtml}</div>`);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut();
    }, 5000);
    
    // Scroll to top to show message
    $('html, body').animate({ scrollTop: 0 }, 300);
}

/**
 * Update cart count in navbar
 */
function updateCartCount(count) {
    $('#cart-count').text(count || 0);
    
    // Add animation
    $('#cart-count').addClass('animate__animated animate__pulse');
    setTimeout(function() {
        $('#cart-count').removeClass('animate__animated animate__pulse');
    }, 1000);
}

/**
 * Update cart count display
 */
function updateCartCountDisplay() {
    // This would typically fetch from server
    // For now, we'll just ensure the display is correct
    const currentCount = $('#cart-count').text();
    if (!currentCount || currentCount === '0') {
        $('#cart-count').text('0');
    }
}

/**
 * Check if user is authenticated
 */
function isUserAuthenticated() {
    // Check if user menu exists in navbar
    return $('.navbar .dropdown-toggle').length > 0;
}

/**
 * Check if user is admin
 */
function isUserAdmin() {
    // Check if admin indicator exists in navbar
    return $('.navbar .dropdown-toggle').text().includes('Admin');
}

/**
 * Get CSRF token
 */
function getCsrfToken() {
    // Try to get from meta tag first
    let token = $('meta[name=csrf-token]').attr('content');
    if (!token) {
        // Fallback to form input
        token = $('[name=csrfmiddlewaretoken]').val();
    }
    if (!token) {
        console.warn('CSRF token not found');
    }
    return token;
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('ne-NP', {
        style: 'currency',
        currency: 'NPR'
    }).format(amount);
}

/**
 * Debounce function for search
 */
function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

/**
 * Initialize search with debounce
 */
function initializeSearch() {
    const searchInput = $('input[name="search"]');
    if (searchInput.length > 0) {
        const debouncedSearch = debounce(function() {
            // Implement live search if needed
            console.log('Searching for:', searchInput.val());
        }, 300);
        
        searchInput.on('input', debouncedSearch);
    }
}

/**
 * Handle responsive navigation
 */
function handleResponsiveNav() {
    // Close mobile menu when clicking outside
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.navbar').length) {
            $('.navbar-collapse').collapse('hide');
        }
    });
}

/**
 * Initialize on page load
 */
$(window).on('load', function() {
    // Hide loading spinner if exists
    $('.loading-spinner').fadeOut();
    
    // Initialize additional components
    initializeSearch();
    handleResponsiveNav();
});

/**
 * Handle scroll events
 */
$(window).on('scroll', function() {
    const scrollTop = $(this).scrollTop();
    
    // Add shadow to navbar on scroll
    if (scrollTop > 50) {
        $('.navbar').addClass('shadow');
    } else {
        $('.navbar').removeClass('shadow');
    }
});

/**
 * Handle window resize
 */
$(window).on('resize', debounce(function() {
    // Handle responsive adjustments
    updateCartCountDisplay();
}, 250));
