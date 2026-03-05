from django.urls import path
from . import views


urlpatterns = [

    # Restaurant Detail
    path(
        "restaurant/<int:id>/",
        views.restaurant_detail,
        name="restaurant_detail"
    ),
    # Book Table flow
    path(
        "restaurant/<int:restaurant_id>/book-table/",
        views.book_table_select_slot,
        name="book_table_select_slot",
    ),
    path(
        "restaurant/<int:restaurant_id>/book-table/map/",
        views.book_table_map,
        name="book_table_map",
    ),
    path(
        "restaurant/<int:restaurant_id>/book-table/success/",
        views.book_table_success,
        name="book_table_success",
    ),

    # Dashboard
    path(
        "admin-dashboard/<int:restaurant_id>/",
        views.restaurant_dashboard,
        name="restaurant_dashboard"
    ),

    # Menu Management
    path(
        "menu/<int:restaurant_id>/",
        views.manage_menu,
        name="manage_menu"   # ✅ changed from "menu" to "manage_menu"
    ),
    path(
    "menu/<int:restaurant_id>/",
    views.menu,
    name="menu"
),


    # Add Category
    path(
        "menu/<int:restaurant_id>/add-category/",
        views.add_category,
        name="add_category"
    ),
     path('menu/<int:restaurant_id>/edit-subcategory/<int:category_id>/',
         views.edit_category, name='edit_category'),

    path('menu/<int:restaurant_id>/delete-subcategory/<int:category_id>/',
         views.delete_category, name='delete_category'),

    # Edit Category
    path(
        "menu/<int:restaurant_id>/category/<int:category_id>/edit/",
        views.edit_category,
        name="edit_category"
    ),

    # Delete Category
    path(
        "menu/<int:restaurant_id>/category/<int:category_id>/delete/",
        views.delete_category,
        name="delete_category"
    ),

    # Add Menu Item
    path(
        "menu/<int:restaurant_id>/add-item/",
        views.add_menu_item,
        name="add_menu_item"
    ),
path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),

    # Edit Menu Item
    path(
        "menu/<int:restaurant_id>/item/<int:item_id>/edit/",
        views.edit_menu_item,
        name="edit_menu_item"
    ),

    # Delete Menu Item
    path(
        "menu/<int:restaurant_id>/item/<int:item_id>/delete/",
        views.delete_menu_item,
        name="delete_menu_item"
    ),

    # Orders
    path(
        "orders/",
        views.order_list,
        name="order_list"
    ),
    # urls.py
     path('menu/<int:restaurant_id>/', views.view_menu, name='view_menu'),

    # Tables (admin: manage tables for this restaurant)
    path(
        "restaurant/<int:restaurant_id>/tables/",
        views.manage_restaurant_tables,
        name="manage_restaurant_tables",
    ),
    # Reservations (admin: view all table bookings)
    path(
        "restaurant/<int:restaurant_id>/reservations/",
        views.view_reservations,
        name="view_reservations",
    ),
    path(
        "tables/",
        views.table_map,
        name="table_map"
    ),

    path(
"admin-dashboard/<int:restaurant_id>/sales/",
views.sales_analytics,
name="sales_reports"
),

    # Waiting List
    path(
"admin-dashboard/<int:restaurant_id>/waiting-list/",
views.waiting_list,
name="waiting_list"
),

    # Settings
    path(
        "settings/",
        views.restaurant_settings,
        name="restaurant_settings"
    ),
    # Walk-in Customer
    path(
        "admin-dashboard/<int:restaurant_id>/walkin/",
        views.handle_walkin_customer,
        name="handle_walkin"
    ),

    # Free Table
    path(
        "table/<int:table_id>/free/",
        views.free_table,
        name="free_table"
    ),

    # Manual Seat
    path(
        "waiting/<int:pk>/seat/",
        views.mark_seated,
        name="mark_seated"
    ),

    # Remove Waiting
    path(
        "waiting/<int:pk>/remove/",
        views.remove_waiting,
        name="remove_waiting"
    ),

    # 🔴 AJAX Waiting Data (ADD THIS)
    path(
        "admin-dashboard/<int:restaurant_id>/waiting-data/",
        views.waiting_data,
        name="waiting_data"
    ),

    path(
    "admin-dashboard/<int:restaurant_id>/stats/",
    views.dashboard_stats,
    name="dashboard_stats"
),
    path(
"restaurant/<int:restaurant_id>/join-waiting/",
views.join_waiting_list,
name="join_waiting"
),

    path(
"settings/",
views.restaurant_settings,
name="restaurant_settings"
),


    
]
