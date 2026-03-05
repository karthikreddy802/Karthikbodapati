from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, Cart, CartItem
from restaurants.models import MenuItem


def on_my_way(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'cooking'
    order.save()
    return redirect('dashboard')


# ===============================
# ADD THESE FUNCTIONS BELOW
# ===============================

@login_required
def add_to_cart(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        menu_item=menu_item
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()

    total = sum(item.get_total_price() for item in cart_items)

    return render(request, "orders/view_cart.html", {
        "cart_items": cart_items,
        "total": total
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from restaurants.models import Restaurant
from .models import Order


@login_required
def restaurant_orders(request):

    # owner restaurant
    restaurant = Restaurant.objects.get(
        owner=request.user
    )

    orders = Order.objects.filter(
        restaurant=restaurant
    ).order_by("-created_at")

    return render(

        request,

        "order_list.html",

        {
            "restaurant": restaurant,
            "orders": orders
        }

    )