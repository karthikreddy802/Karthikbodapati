from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import FeedbackForm, RegistrationForm
from .models import CafeItem, MenuItem, Feedback


# ---------------- HOME ----------------
def home(request):
    return render(request, 'food/home.html')


# ---------------- AUTH ----------------
def logout_view(request):
    logout(request)
    return render(request, 'food/logout.html')


def login_page(request):
    return render(request, 'food/login.html')


def register_view(request):
    form = RegistrationForm()

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(user.password)
            user.save()
            return redirect('login')  # change if your login url name differs

    return render(request, 'food/register.html', {'form': form})


# ---------------- MENU ----------------
def menu_view(request):
    menu_items = MenuItem.objects.filter(is_available=True)
    return render(request, 'food/menu.html', {'menu_items': menu_items})


def cafe(request):
    menu = CafeItem.objects.all()
    return render(request, 'food/cafe.html', {'menu': menu})


# ---------------- FEEDBACK ----------------
def submit_feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedback_list')
    else:
        form = FeedbackForm()

    return render(request, "food/submit_feedback.html", {"form": form})


@login_required
def feedback_list(request):
    feedbacks = Feedback.objects.all().order_by("-created_at")
    return render(request, "food/feedback_list.html", {"feedbacks": feedbacks})


# ---------------- CART (SESSION BASED) ----------------
def add_to_cart(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)

    if item_id in cart:
        cart[item_id] += 1
    else:
        cart[item_id] = 1

    request.session['cart'] = cart
    return redirect('cart_items')


def cart_items(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for item_id, qty in cart.items():
        try:
            item = CafeItem.objects.get(id=item_id)
            item.quantity = qty
            item.total_price = item.price * qty
            total += item.total_price
            items.append(item)
        except CafeItem.DoesNotExist:
            pass

    return render(request, "food/cart.html", {
        "items": items,
        "total": total
    })


def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    item_id = str(item_id)

    if item_id in cart:
        del cart[item_id]

    request.session['cart'] = cart
    return redirect('cart_items')


def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart_items')


# ---------------- STATIC PAGES ----------------
def my_story(request):
    return render(request, 'food/story.html')

