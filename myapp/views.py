
from django.shortcuts import render, redirect, get_object_or_404,reverse
from .models import Product,OrderDetal
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponseNotFound


import json 
import stripe

def index(request):
    products = Product.objects.all()
    return render(request, "myapp/index.html", {'products': products})

def detail(request, id):
    product = get_object_or_404(Product, id=id)
    strip_p_k="pk_test_51LWjmsGP3Q91Y1OskAZTyuhqap7y63QPpjLlUXYsBdj17VtIklfT2Ero39WvGUIiddKlNz52fUtCPobNE8CV79bh00zxisj2Np"
    return render(request, "myapp/detail.html", {'product': product,'strip_p_k':strip_p_k})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Initialize cart in session if not present
    if 'cart' not in request.session:
        request.session['cart'] = {}

    # Add product to cart
    if str(product.id) in request.session['cart']:
        request.session['cart'][str(product.id)] += 1  # Increment quantity if already in cart
    else:
        request.session['cart'][str(product.id)] = 1  # Set quantity to 1

    request.session.modified = True  # Mark the session as modified
    return redirect('index')  # Redirect to index or any other page

def cart(request):
    cart_items = request.session.get('cart', {})
    print(cart_items)
    products = Product.objects.filter(id__in=cart_items.keys())
    
    total = sum(product.price * quantity for product, quantity in zip(products, cart_items.values()))
    strip_p_k=settings.STRIPE_PUBLISHABLE_KEY  # Correct usage

    
    return render(request, 'myapp/cart.html', {
        'products': products,
        'cart_items': cart_items,
        'total': total,'strip_p_k':strip_p_k
    })

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]  # Remove item from cart
        request.session.modified = True
    return redirect('cart')  # Redirect to cart
@csrf_exempt
def create_checkout_session(request, id):
    if request.method == 'POST':
        try:
            # Parse JSON data from request
            request_data = json.loads(request.body)
            
            # Set Stripe API key
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Fetch the product
            product = Product.objects.get(id=id)
            
            # Create Stripe Checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': product.name,
                            },
                            'unit_amount': int(product.price * 100),  # Use product price, not name
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('success')) +
                            "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=request.build_absolute_uri(reverse('failed')),
                customer_email=request_data['email'],
            )
            
            # Create and save order
            order = OrderDetal()
            order.customer_email = request_data['email']
            order.product = product
            order.stripe_payment_intent = checkout_session['payment_intent']
            order.amount = int(product.price)
            order.save()

            # Return session ID to the client
            return JsonResponse({'sessionId': checkout_session.id})
        
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def payment_sucess_view(request):
    session_id=request.GET.get('session_id')
    if session_id is None:
        return HttpResponseNotFound()
    strip.api_key=settings.STRIP_SECRET_KEY
    session=strip.checkout.Session.retrieve(session_id)
    order=get_object_or_404 (OrderDetal,strip_payment_intent=session.payment_intent)
    order.has_paid=True
    order.save()
    return render(request,'myapp/success.html',{'order':order})


def payment_failed_view(request):
    return render(request,'myapp/failed.html')
