from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.choose_login, name="signup"),
    path("customer-signup/", views.customer_signup, name="customer_signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("restaurant-owner-login/", views.RestaurantOwnerLoginView.as_view(), name="restaurant_owner_login"),
    path("logout/", views.logout_view, name="logout"),

    # Main Dashboard (handles all roles)
    path("dashboard/", views.dashboard, name="dashboard"),

    # Superadmin
    path("superadmin-dashboard/", views.superadmin_dashboard, name="superadmin_dashboard"),

    # Admin Management
    path("manage-restaurants/", views.manage_restaurants, name="manage_restaurants"),
    path("manage-users/", views.manage_users, name="manage_users"),
    path("restaurant-requests/", views.restaurant_requests, name="restaurant_requests"),
    path("all-orders/", views.all_orders, name="all_orders"),

    path("add-restaurant/", views.add_restaurant, name="add_restaurant"),
    path("request-restaurant/", views.request_restaurant, name="request_restaurant"),
    path(
        "request-restaurant/success/",
        views.request_restaurant_success,
        name="request_restaurant_success",
    ),
    path("toggle-user/<int:user_id>/", views.toggle_user_status, name="toggle_user"),
    path("edit-restaurant/<int:id>/", views.edit_restaurant, name="edit_restaurant"),
    path("delete-restaurant/<int:id>/", views.delete_restaurant, name="delete_restaurant"),
    path(
        "restaurant-owner-signup/",
        views.restaurant_owner_signup,
        name="restaurant_owner_signup",
    ),
]
