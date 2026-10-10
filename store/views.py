
from django.shortcuts import render, redirect
from django.db import transaction
from .models import Product, Order, OrderItem


def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/products.html', {'products': products})



def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('product_list')

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return redirect('product_list')

    cart_data = request.session.get('cart', {})
    product_key = str(product_id)
    current_quantity = int(cart_data.get(product_key, 0))

    if current_quantity < product.stock:
        cart_data[product_key] = current_quantity + 1

    request.session['cart'] = cart_data
    request.session.modified = True

    return redirect('cart')




def remove_from_cart(request, product_id):
    cart_data = request.session.get('cart', {})
    cart_data.pop(str(product_id), None)
    request.session['cart'] = cart_data
    request.session.modified = True
    return redirect('cart')


def increase_quantity(request, product_id):
    cart_data = request.session.get('cart', {})
    product_key = str(product_id)

    try:
        product = Product.objects.get(id=product_id)
        quantity = int(cart_data.get(product_key, 0))

        if quantity < product.stock:
            cart_data[product_key] = quantity + 1
    except Product.DoesNotExist:
        cart_data.pop(product_key, None)

    request.session['cart'] = cart_data
    request.session.modified = True
    return redirect('cart')


def decrease_quantity(request, product_id):
    cart_data = request.session.get('cart', {})
    product_key = str(product_id)

    if product_key in cart_data:
        quantity = int(cart_data[product_key])

        if quantity > 1:
            cart_data[product_key] = quantity - 1
        else:
            del cart_data[product_key]

    request.session['cart'] = cart_data
    request.session.modified = True
    return redirect('cart')


def cart(request):
    cart_data = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=int(product_id))
            quantity = int(quantity)
        except (Product.DoesNotExist, ValueError, TypeError):
            continue

        if quantity < 1:
            continue

        subtotal = product.price * quantity
        total += subtotal

        items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return render(request, 'store/cart.html', {
        'items': items,
        'total': total,
    })




def checkout(request):
    cart_data = request.session.get('cart', {})
    products_in_cart = []
    total = 0

    print("CHECKOUT SESSION CART:", cart_data)

    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=int(product_id))
            quantity = int(quantity)
        except (Product.DoesNotExist, ValueError, TypeError):
            continue

        if quantity < 1:
            continue

        products_in_cart.append((product, quantity))
        total += product.price * quantity

    print("PRODUCTS FOUND:", len(products_in_cart))

    if not products_in_cart:
        return render(request, 'store/cart.html', {
            'items': [],
            'total': 0,
            'error': 'Your cart is empty. Please add a product first.',
        })

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not all([name, email, phone, address]):
            return render(request, 'store/checkout.html', {
                'total': total,
                'error': 'Please fill in all the fields.',
            })

        with transaction.atomic():
            order = Order.objects.create(
                name=name,
                email=email,
                phone=phone,
                address=address,
                total=total,
            )

            for product, quantity in products_in_cart:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price,
                )

        request.session['order'] = {
            'id': order.id,
            'name': order.name,
            'email': order.email,
            'phone': order.phone,
            'address': order.address,
            'total': float(order.total),
        }

        request.session['cart'] = {}
        request.session.modified = True

        return redirect('order_success')

    return render(request, 'store/checkout.html', {'total': total})



def order_success(request):
    order = request.session.get('order')

    if not order:
        return redirect('product_list')

    return render(request, 'store/order_success.html', {'order': order})
