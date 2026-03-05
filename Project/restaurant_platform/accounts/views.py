from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from orders.models import Order
from restaurants.models import Restaurant

from .forms import CustomAuthenticationForm, CustomUserCreationForm
User = get_user_model()
import math

User = get_user_model()


# ==============================
# 🔹 SIGNUP
# ==============================


def customer_signup(request):
    """
    Customer registration page - shown when users click register from login page.
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure role is set to customer
            user.role = "customer"
            user.save()
            login(request, user)
            # Redirect to the shared role-based dashboard (customers see restaurant list)
            return redirect("dashboard")

    else:
        form = CustomUserCreationForm()

    return render(request, "signup.html", {"form": form})


def choose_login(request):
    """
    Simple page that lets the user choose between
    customer login and restaurant owner login.
    """
    return render(request, "choose_login.html")


def restaurant_owner_signup(request):
    """
    Signup flow for restaurant owners. Creates a user with
    role=restaurant_admin and a pending Restaurant record.
    """

    if request.method == "POST":
        restaurant_name = request.POST.get("restaurant_name")
        address = request.POST.get("address")
        map_url = request.POST.get("map_url")
        owner_name = request.POST.get("owner_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Use email as username to keep it simple
        username = email

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.first_name = owner_name
        user.role = "restaurant_admin"
        # Store phone in last_name for now (no dedicated field)
        user.last_name = phone
        user.save()

        restaurant = Restaurant.objects.create(
            name=restaurant_name,
            location=address,
            map_url=map_url,
            owner=user,
            status=Restaurant.STATUS_PENDING,
        )

        # Link user to this restaurant
        user.restaurant = restaurant
        user.save()

        login(request, user)
        return redirect("request_restaurant_success")

    return render(request, "restaurant_owner_signup.html")


# ==============================
# 🔹 LOGIN
# ==============================
class CustomLoginView(LoginView):
    template_name = "login.html"
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        """
        Customer login: prevent restaurant owners from logging in here.
        """
        user = form.get_user()
        if getattr(user, "role", None) == "restaurant_admin":
            messages.error(self.request, "Please use Restaurant Owner Login.")
            return redirect("restaurant_owner_login")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("dashboard")


class RestaurantOwnerLoginView(LoginView):
    template_name = "resturant_owner_login.html"
    authentication_form = CustomAuthenticationForm

    def form_valid(self, form):
        """
        Restaurant owner login: only allow restaurant_admin accounts.
        """
        user = form.get_user()
        if getattr(user, "role", None) != "restaurant_admin":
            messages.error(self.request, "This account is not a restaurant owner. Please use Customer Login.")
            return redirect("login")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("dashboard")


# ==============================
# 🔹 ROLE BASED DASHBOARD
# ==============================
from restaurants.models import Restaurant

@login_required
def dashboard(request):

    # SUPER ADMIN
    if request.user.role == "superadmin":
        return redirect("superadmin_dashboard")

    # RESTAURANT ADMIN
    elif request.user.role == "restaurant_admin":
        restaurant = Restaurant.objects.filter(user=request.user).first()

        if restaurant:
            return redirect("restaurant_dashboard", restaurant_id=restaurant.id)
        else:
            messages.error(request, "No restaurant assigned to you.")
            return redirect("home")

    # CUSTOMER DASHBOARD
# Only show restaurants that are approved by Super Admin
    restaurants = Restaurant.objects.filter(status=Restaurant.STATUS_APPROVED)
    name = request.GET.get("restaurant_name")
    city = request.GET.get("city")

    if name:
        restaurants = restaurants.filter(name__icontains=name)

    if city:
        restaurants = restaurants.filter(location__icontains=city)

    orders = Order.objects.filter(customer=request.user)

    return render(request, "customer/dashboard.html", {
        "restaurants": restaurants,
        "orders": orders
    })


# ==============================
# 🔹 SUPERADMIN DASHBOARD
# ==============================
@login_required
def superadmin_dashboard(request):

    total_restaurants = Restaurant.objects.count()
    total_users = User.objects.count()
    total_admins = User.objects.filter(role="restaurant_admin").count()
    total_orders = Order.objects.count()

    total_revenue = Order.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    pending_requests = Restaurant.objects.filter(status=Restaurant.STATUS_PENDING)


    context = {
        "total_restaurants": total_restaurants,
        "total_users": total_users,
        "total_admins": total_admins,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_count": pending_requests.count(),

    }

    return render(request, "superAdmin/dashboard.html", context)



# ==============================
# 🔹 LOGOUT
# ==============================
def logout_view(request):
    logout(request)
    return redirect("login")


# ==============================
# 🔹 HAVERSINE FUNCTION
# ==============================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)

    a = (
        math.sin(dLat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dLon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

from restaurants.models import Restaurant
from django.contrib.auth import get_user_model
from orders.models import Order

User = get_user_model()


@login_required
def manage_restaurants(request):
    restaurants = Restaurant.objects.all()
    return render(request, "superAdmin/manage_restaurants.html", {
        "restaurants": restaurants
    })


@login_required
def manage_users(request):
    users = User.objects.all()
    return render(request, "manage_users.html", {
        "users": users
    })


@login_required
def restaurant_requests(request):
    """
    Super Admin view to approve / reject restaurant requests
    submitted by owners.
    """

    if request.user.role != "superadmin":
        return redirect("dashboard")

    if request.method == "POST":
        action = request.POST.get("action")
        restaurant_id = request.POST.get("restaurant_id")
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        if action == "approve":
            restaurant.status = Restaurant.STATUS_APPROVED
            restaurant.save()

            # If this restaurant has an owner, promote them to restaurant_admin
            if restaurant.owner:
                restaurant.owner.role = "restaurant_admin"
                restaurant.owner.restaurant = restaurant
                restaurant.owner.save()

        elif action == "reject":
            restaurant.status = Restaurant.STATUS_REJECTED
            restaurant.save()

        return redirect("restaurant_requests")

    pending_restaurants = Restaurant.objects.filter(status=Restaurant.STATUS_PENDING)

    return render(
        request,
        "superAdmin/restaurant_requests.html",
         {"pending_restaurants": pending_restaurants},
    )

    total_restaurants = Restaurant.objects.count()

    return render(request, "superAdmin/system_reports.html", {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_restaurants": total_restaurants,
    })


@login_required
def all_orders(request):
    orders = Order.objects.all().order_by("-id")
    return render(request, "superAdmin/all_orders.html", {
        "orders": orders
    })
from restaurants.models import Restaurant


def add_restaurant(request):
    if request.method == "POST":
        name = request.POST.get("name")
        location = request.POST.get("location")
        map_url = request.POST.get("map_url")

        Restaurant.objects.create(
            name=name,
            location=location,
             map_url=map_url,
            status=Restaurant.STATUS_APPROVED,
        
        )

        return redirect("manage_restaurants")

    return render(request, "superAdmin/add_restaurant.html")

@login_required
def request_restaurant(request):
    """
    Allow any logged-in user to request that their restaurant
    be added to the platform. This will be created in a
    'pending' state and must be approved by the Super Admin.
    """

    if request.method == "POST":
        name = request.POST.get("name")
        location = request.POST.get("location")
        map_url = request.POST.get("map_url")

        Restaurant.objects.create(
            name=name,
            location=location,
            map_url=map_url,
            owner=request.user,
            status=Restaurant.STATUS_PENDING,
        )

        return redirect("request_restaurant_success")

    return render(request, "request_restaurant.html")


@login_required
def request_restaurant_success(request):
    """
    Simple confirmation page after a restaurant request is submitted.
    """
    return render(request, "request_restaurant_success.html")

def edit_restaurant(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)

    if request.method == "POST":
        restaurant.name = request.POST.get("name")
        restaurant.location = request.POST.get("location")
        restaurant.map_url = request.POST.get("map_url")
        restaurant.save()

        return redirect("manage_restaurants")

    return render(request, "superAdmin/edit_restaurant.html", {"restaurant": restaurant})
def restaurant_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'restaurant_admin':
            return HttpResponseForbidden("You are not allowed to access this page")
        return view_func(request, *args, **kwargs)
    return wrapper



def delete_restaurant(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)
    restaurant.delete()
    return redirect("manage_restaurants")
@login_required
def toggle_user_status(request, user_id):

    # ✅ Only Super Admin can perform this action
    if request.user.role != "superadmin":
        return redirect("dashboard")

    user = get_object_or_404(User, id=user_id)

    # ❌ Prevent Super Admin from being deactivated
    if user.role == "superadmin":
        return redirect("manage_users")

    user.is_active = not user.is_active
    user.save()

    return redirect("manage_users")