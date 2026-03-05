from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Restaurant, MenuItem, MenuCategory, Table
from .forms import MenuItemForm, MenuCategoryForm
from reservations.models import Reservation
from .models import MenuItem, Cart

# Time slots for table booking (display label, value)
BOOKING_SLOTS = [
    ("10-12", "10:00 AM - 12:00 PM"),
    ("12-14", "12:00 PM - 2:00 PM"),
    ("14-16", "2:00 PM - 4:00 PM"),
    ("18-20", "6:00 PM - 8:00 PM"),
    ("20-22", "8:00 PM - 10:00 PM"),
]

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Restaurant


@login_required
def restaurant_settings(request):

    restaurant = Restaurant.objects.filter(
        owner=request.user
    ).first()

    if not restaurant:

        messages.error(
            request,
            "No restaurant assigned."
        )

        return redirect("admin_dashboard")

    if request.method == "POST":

        restaurant.name = request.POST.get("name")

        restaurant.location = request.POST.get("location")

        restaurant.map_url = request.POST.get("map_url")

        restaurant.description = request.POST.get(
            "description"
        )

        restaurant.phone = request.POST.get(
            "phone"
        )

        restaurant.opening_time = request.POST.get(
            "opening_time"
        )

        restaurant.closing_time = request.POST.get(
            "closing_time"
        )

        restaurant.is_open = True if request.POST.get(
            "is_open"
        ) else False

        restaurant.save()

        messages.success(
            request,
            "Restaurant Updated Successfully ✅"
        )

        return redirect("restaurant_settings")

    return render(

        request,

        "settings.html",

        {
            "restaurant": restaurant
        }

    )
# 🔹 Restaurant Detail
@login_required(login_url='/login/')
def restaurant_detail(request, id):
    restaurant = get_object_or_404(Restaurant, id=id)

    return render(request, "restaurant_detail.html", {
        "restaurant": restaurant
    })


# 🔹 Restaurant Dashboard
@login_required(login_url='/login/')
def restaurant_dashboard(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    return render(request, "admin_dashboard.html", {
        "restaurant": restaurant
    })
@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        item=item
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('manage_menu', restaurant_id=item.category.restaurant.id)

# 🔹 Manage Menu
@login_required(login_url='/login/')
def manage_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)

    # All categories for this restaurant (no parent filter - works even without parent_id column)
    categories = MenuCategory.objects.filter(restaurant=restaurant).order_by('name')

    return render(request, 'manage_menu.html', {
        'restaurant': restaurant,
        'categories': categories
    })




# 🔹 Add Category
@login_required
def add_category(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == "POST":
        form = MenuCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.restaurant = restaurant
            category.save()
            return redirect('manage_menu', restaurant_id=restaurant.id)
    else:
        form = MenuCategoryForm()

    return render(request, 'add_category.html', {
        'form': form,
        'restaurant': restaurant
    })




@login_required

def edit_category(request, restaurant_id, category_id):
    category = get_object_or_404(MenuCategory, id=category_id)
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.save()
        return redirect('manage_menu', restaurant_id=restaurant.id)

    return render(request, 'restaurants/edit_category.html', {
        'category': category,
        'restaurant': restaurant
    })


@login_required
def delete_category(request, restaurant_id, category_id):
    category = get_object_or_404(MenuCategory, id=category_id)
    category.delete()
    return redirect('manage_menu', restaurant_id=restaurant_id)



# 🔹 Add Menu Item
@login_required
def add_menu_item(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == "POST":
        form = MenuItemForm(request.POST, restaurant=restaurant)
        if form.is_valid():
            item = form.save(commit=False)
            item.category = form.cleaned_data["category"]  # ✅ category links restaurant
            item.restaurant = restaurant
            item.save()
            return redirect("manage_menu", restaurant_id=restaurant.id)
    else:
        form = MenuItemForm(restaurant=restaurant)

    return render(request, "form.html", {
        "form": form,
        "restaurant": restaurant
    })


@login_required
def edit_menu_item(request, restaurant_id, item_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)

    if request.method == "POST":
        form = MenuItemForm(request.POST, instance=item, restaurant=restaurant)
        if form.is_valid():
            form.save()
            return redirect("manage_menu", restaurant_id=restaurant.id)
    else:
        form = MenuItemForm(instance=item, restaurant=restaurant)

    return render(request, "form.html", {
        "form": form,
        "restaurant": restaurant
    })


@login_required
def delete_menu_item(request, restaurant_id, item_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)
    item.delete()

    return redirect("manage_menu", restaurant_id=restaurant.id)


from django.shortcuts import render, get_object_or_404
from .models import Restaurant, MenuItem

def menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    # Get all menu items for this restaurant (no parent filter needed)
    items = MenuItem.objects.filter(
        category__restaurant=restaurant,
        available=True
    ).select_related("category").order_by("category__name", "name")

    return render(request, "menu.html", {
        "restaurant": restaurant,
        "items": items
    })




# 🔹 Other simple views
def order_list(request):
    return render(request, "order_list.html")

def table_map(request):
    return render(request, "table_map.html")

from django.db.models import Sum
from django.utils import timezone
from orders.models import Order



@login_required
def sales_analytics(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id
    )

    orders = Order.objects.filter(
        restaurant=restaurant
    )

    total_revenue = orders.filter(
        status="Completed"
    ).aggregate(
        Sum("total_price")
    )["total_price__sum"] or 0


    today_sales = orders.filter(

        status="Completed",

        created_at__date=
        timezone.now().date()

    ).aggregate(
        Sum("total_price")
    )["total_price__sum"] or 0


    context = {

        "restaurant": restaurant,

        "orders": orders.order_by("-created_at"),

        "total_revenue": total_revenue,

        "today_sales": today_sales,

        "total_orders": orders.count(),

    }

    return render(
request,
"sales_reports.html",
context
)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import WaitingList, Table, Restaurant



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import WaitingList, Restaurant


@login_required
def waiting_list(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id
    )

    waiting_customers = WaitingList.objects.filter(

        restaurant=restaurant,

        status="waiting"

    ).order_by("created_at")


    context = {

        "restaurant": restaurant,

        "waiting_list": waiting_customers,

        "waiting_count": waiting_customers.count(),

    }

    return render(

        request,

        "waiting_list.html",

        context

    )


@login_required
def waiting_data(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id
    )

    waiting_customers = WaitingList.objects.filter(

        restaurant=restaurant,

        status="waiting"

    ).order_by("created_at")


    data = []

    AVERAGE_DINING_TIME = 45


    for index, customer in enumerate(waiting_customers):

        estimated_time = (index + 1) * AVERAGE_DINING_TIME

        data.append({

            "id": customer.id,

            "name": customer.name,

            "phone": customer.phone,

            "guests": customer.guests,

            "time": customer.created_at.strftime("%I:%M %p"),

            "estimated_wait": estimated_time,

        })


    return JsonResponse({

        "waiting_count": waiting_customers.count(),

        "customers": data

    })


@login_required
def handle_walkin_customer(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id
    )

    if request.method == "POST":

        name = request.POST.get("name")

        phone = request.POST.get("phone")

        guests = int(request.POST.get("guests"))


        # ===========================
        # 1️⃣ Try Single Table First
        # ===========================

        table = Table.objects.filter(

            restaurant=restaurant,

            status='available',

            capacity__gte=guests

        ).order_by('capacity').first()


        if table:

            table.status = 'occupied'

            table.save()

            messages.success(

                request,

                f"Table {table.table_number} assigned successfully!"

            )


        else:

            # ===========================
            # 2️⃣ Smart Table Merge
            # ===========================

            tables = Table.objects.filter(

                restaurant=restaurant,

                status='available'

            ).order_by('capacity')


            total_capacity = 0

            selected_tables = []


            for t in tables:

                selected_tables.append(t)

                total_capacity += t.capacity

                if total_capacity >= guests:

                    break


            # Enough combined tables
            if total_capacity >= guests:

                for t in selected_tables:

                    t.status = 'occupied'

                    t.save()

                messages.success(

                    request,

                    "Multiple tables combined and assigned successfully!"

                )


            else:

                # ===========================
                # 3️⃣ Add Waiting List
                # ===========================

                if not WaitingList.objects.filter(

                    restaurant=restaurant,

                    phone=phone,

                    status='waiting'

                ).exists():

                    WaitingList.objects.create(

                        restaurant=restaurant,

                        name=name,

                        phone=phone,

                        guests=guests,

                        status='waiting'

                    )

                    messages.warning(

                        request,

                        "All tables are full. Customer added to waiting list."

                    )

                else:

                    messages.warning(

                        request,

                        "Customer already in waiting list."

                    )


    return redirect(

        "restaurant_dashboard",

        restaurant_id=restaurant.id

    )

@login_required
def free_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)

    table.status = 'available'
    table.save()

    # Find first waiting customer that fits
    waiting_customer = WaitingList.objects.filter(
        restaurant=table.restaurant,
        status='waiting',
        guests__lte=table.capacity
    ).order_by('created_at').first()

    if waiting_customer:
        table.status = 'occupied'
        table.save()

        waiting_customer.status = 'seated'
        waiting_customer.save()

        messages.success(
            request,
            f"{waiting_customer.name} seated at Table {table.table_number}"
        )

    return redirect("manage_tables", restaurant_id=table.restaurant.id)
@login_required
def mark_seated(request, pk):
    waiting_customer = get_object_or_404(WaitingList, pk=pk)

    table = Table.objects.filter(
        restaurant=waiting_customer.restaurant,
        status='available',
        capacity__gte=waiting_customer.guests
    ).order_by('capacity').first()

    if table:
        table.status = 'occupied'
        table.save()

        waiting_customer.status = 'seated'
        waiting_customer.save()

        messages.success(
            request,
            f"{waiting_customer.name} seated at Table {table.table_number}"
        )
    else:
        messages.warning(
            request,
            "No available table for this customer."
        )

    return redirect("waiting_list", restaurant_id=waiting_customer.restaurant.id)
@login_required
def remove_waiting(request, pk):
    waiting_customer = get_object_or_404(WaitingList, pk=pk)

    waiting_customer.status = 'cancelled'
    waiting_customer.save()

    messages.info(
        request,
        f"{waiting_customer.name} removed from waiting list."
    )

    return redirect("waiting_list", restaurant_id=waiting_customer.restaurant.id)

@login_required
def dashboard_stats(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id
    )

    total_tables = restaurant.tables.count()

    occupied_tables = restaurant.tables.filter(
        status='occupied'
    ).count()

    occupancy_percentage = 0

    if total_tables > 0:
        occupancy_percentage = (
            occupied_tables / total_tables
        ) * 100

    return JsonResponse({

        "occupancy_percentage":
        round(occupancy_percentage,2)
    })

@login_required
def join_waiting_list(request, restaurant_id):

    restaurant = get_object_or_404(
        Restaurant,
        id=restaurant_id
    )

    user = request.user


    # Already waiting?
    existing = WaitingList.objects.filter(

        restaurant=restaurant,

        phone=user.username,

        status="waiting"

    ).first()


    if existing:

        messages.warning(

            request,

            "You are already in waiting list."

        )

        return redirect(
            "restaurant_detail",
            id=restaurant.id
        )


    # Check available tables
    table = Table.objects.filter(

        restaurant=restaurant,

        status="available"

    ).first()


    if table:

        messages.success(

            request,

            "Tables available. Please book directly."

        )

        return redirect(
            "restaurant_detail",
            id=restaurant.id
        )


    # Add to waiting list
    customer = WaitingList.objects.create(

        restaurant=restaurant,

        name=user.username,

        phone=user.username,

        guests=2,

        status="waiting"

    )


    # Queue position
    queue = WaitingList.objects.filter(

        restaurant=restaurant,

        status="waiting"

    ).order_by("created_at")


    position = list(queue).index(customer) + 1


    # Estimated wait
    AVERAGE_DINING_TIME = 45

    estimated_wait = position * AVERAGE_DINING_TIME


    messages.success(

        request,

        f"✅ Joined waiting list!\n"
        f"Queue Position : {position}\n"
        f"Estimated Wait : {estimated_wait} mins"

    )


    return redirect(
        "restaurant_detail",
        id=restaurant.id
    )



def restaurant_settings(request):
    return render(request, "settings.html")

def view_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    # Get all menu items for this restaurant (no parent filter needed)
    items = MenuItem.objects.filter(
        category__restaurant=restaurant,
        available=True
    ).select_related("category").order_by("category__name", "name")
    
    return render(request, "menu.html", {
        "restaurant": restaurant,
        "items": items
    })


# 🔹 Book Table - Step 1: Select date, slot, guests
@login_required(login_url='/login/')
def book_table_select_slot(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == "POST":
        date = request.POST.get("date")
        slot = request.POST.get("slot")
        guests = request.POST.get("guest_count", "2")
        if date and slot:
            url = reverse("book_table_map", args=[restaurant_id]) + f"?date={date}&slot={slot}&guests={guests}"
            return redirect(url)
        messages.error(request, "Please select date and slot.")
    from django.utils import timezone
    today = timezone.localdate().isoformat()
    return render(request, "book_table_select_slot.html", {
        "restaurant": restaurant,
        "slots": BOOKING_SLOTS,
        "today": today,
    })


# 🔹 Book Table - Step 2: Live table map for selected slot
@login_required(login_url='/login/')
def book_table_map(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    date = request.GET.get("date")
    slot = request.GET.get("slot")
    guests = request.GET.get("guests", "2")
    if not date or not slot:
        messages.error(request, "Missing date or slot.")
        return redirect("book_table_select_slot", restaurant_id=restaurant_id)

    tables = Table.objects.filter(restaurant=restaurant).order_by("table_number")
    # If no tables exist, create default tables so the live view is visible
    if not tables.exists():
        for i in range(1, 9):
            Table.objects.create(
                restaurant=restaurant,
                table_number=i,
                capacity=4,
                x_position=(i - 1) % 4 * 80,
                y_position=(i - 1) // 4 * 80,
            )
        tables = Table.objects.filter(restaurant=restaurant).order_by("table_number")
    reserved_table_ids = set(
        Reservation.objects.filter(
            restaurant=restaurant,
            date=date,
            slot=slot,
        ).values_list("table_id", flat=True)
    )

    table_list = []
    for t in tables:
        table_list.append({
            "table": t,
            "is_reserved": t.id in reserved_table_ids,
            "can_book": t.id not in reserved_table_ids and t.capacity >= int(guests or 2),
        })

    if request.method == "POST":
        table_id = request.POST.get("table_id")
        if table_id:
            table = get_object_or_404(Table, id=table_id, restaurant=restaurant)
            if table.id in reserved_table_ids:
                messages.error(request, "This table is already booked for the selected slot.")
            elif table.capacity < int(guests or 2):
                messages.error(request, "Table capacity is less than guest count.")
            else:
                Reservation.objects.create(
                    customer=request.user,
                    restaurant=restaurant,
                    table=table,
                    date=date,
                    slot=slot,
                    guest_count=int(guests or 2),
                )
                messages.success(request, "Table booked successfully!")
                return redirect("book_table_success", restaurant_id=restaurant_id)
        else:
            messages.error(request, "Please select a table.")

    return render(request, "book_table_map.html", {
        "restaurant": restaurant,
        "table_list": table_list,
        "date": date,
        "slot": slot,
        "slot_label": dict(BOOKING_SLOTS).get(slot, slot),
        "guests": guests,
        "customer_name": request.user.get_full_name() or request.user.username,
    })


# 🔹 Book Table - Success
@login_required(login_url='/login/')
def book_table_success(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    return render(request, "book_table_success.html", {"restaurant": restaurant})


# 🔹 Manage Tables (restaurant admin: add/edit/delete tables for live map)
@login_required(login_url='/login/')
def manage_restaurant_tables(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    tables = Table.objects.filter(restaurant=restaurant).order_by("table_number")

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add":
            table_number = request.POST.get("table_number")
            capacity = request.POST.get("capacity", "4")
            if table_number:
                Table.objects.create(
                    restaurant=restaurant,
                    table_number=int(table_number),
                    capacity=int(capacity or 4),
                )
                messages.success(request, "Table added.")
        elif action == "delete":
            tid = request.POST.get("table_id")
            if tid:
                t = Table.objects.filter(id=tid, restaurant=restaurant).first()
                if t:
                    t.delete()
                    messages.success(request, "Table removed.")

        return redirect("manage_restaurant_tables", restaurant_id=restaurant_id)

    return render(request, "manage_restaurant_tables.html", {
        "restaurant": restaurant,
        "tables": tables,
    })


# 🔹 View Reservations (restaurant admin: see all table bookings)
@login_required(login_url='/login/')
def view_reservations(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    from django.utils import timezone
    from django.db.models import Q
    
    # Get all reservations for this restaurant, ordered by date and slot
    reservations = Reservation.objects.filter(restaurant=restaurant).order_by("date", "slot")
    
    # Filter options
    filter_type = request.GET.get("filter", "all")
    today = timezone.localdate()
    
    if filter_type == "today":
        reservations = reservations.filter(date=today)
    elif filter_type == "upcoming":
        reservations = reservations.filter(date__gte=today)
    elif filter_type == "past":
        reservations = reservations.filter(date__lt=today)
    
    # Add slot label to each reservation for template display
    slot_labels_dict = dict(BOOKING_SLOTS)
    reservations_list = []
    for r in reservations:
        r.slot_label = slot_labels_dict.get(r.slot, r.slot)
        reservations_list.append(r)
    
    return render(request, "view_reservations.html", {
        "restaurant": restaurant,
        "reservations": reservations_list,
        "filter_type": filter_type,
        "today": today,
    })
@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        item=item
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('manage_menu', restaurant_id=item.category.restaurant.id)